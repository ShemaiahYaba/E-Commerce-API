"""Order service: create from cart, list, get, admin status update, payment_intent simulation."""

import uuid
from decimal import Decimal
from typing import List

from database import db
from models import Order, OrderItem, CartItem, Product
from exceptions import OrderNotFoundError, ValidationError
from validators import OrderValidator
from services.base_service import BaseService
from models import User
from config.mail import mail
from flask_mail import Message
from flask import current_app


def _get_cart_items(user_id: int) -> List[CartItem]:
    """Return cart items for user; raise ValidationError if empty."""
    items = CartItem.query.filter_by(user_id=user_id).all()
    OrderValidator.validate_cart_not_empty(items)
    return items


def _verify_cart_stock(cart_items: List[CartItem]) -> None:
    """Raise ValidationError if any cart item exceeds product stock."""
    OrderValidator.validate_cart_stock(cart_items)


def _calculate_cart_total(cart_items: List[CartItem]) -> Decimal:
    """Return total price of all cart items."""
    total = Decimal("0")
    for ci in cart_items:
        product = db.session.get(Product, ci.product_id)
        total += product.price * ci.quantity
    return total


def _generate_payment_intent_id() -> str:
    """Return a simulated payment intent id."""
    return f"pi_sim_{uuid.uuid4().hex[:24]}"


def _create_order_object(user_id: int, total: Decimal, payment_intent_id: str) -> Order:
    """Create Order instance, add to session, flush; return order."""
    order = Order(
        user_id=user_id,
        status="pending",
        total=total,
        payment_intent_id=payment_intent_id,
    )
    db.session.add(order)
    db.session.flush()
    return order


def _create_order_items_from_cart(order: Order, cart_items: List[CartItem]) -> None:
    """Create OrderItem rows from cart items and add to session."""
    for ci in cart_items:
        product = db.session.get(Product, ci.product_id)
        oi = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=ci.quantity,
            price=product.price,
        )
        db.session.add(oi)


def _decrement_product_stock(cart_items: List[CartItem]) -> None:
    """Decrement stock for each product in cart items."""
    for ci in cart_items:
        product = db.session.get(Product, ci.product_id)
        product.stock -= ci.quantity


def _clear_user_cart(user_id: int) -> None:
    """Remove all cart items for user."""
    CartItem.query.filter_by(user_id=user_id).delete()


def create_order(user_id: int, payment_intent_id: str | None = None) -> Order:
    """Create order from cart; decrement stock, clear cart. Uses provided intent or simulates."""
    cart_items = _get_cart_items(user_id)
    _verify_cart_stock(cart_items)
    total = _calculate_cart_total(cart_items)
    if not payment_intent_id:
        payment_intent_id = _generate_payment_intent_id()

    order = _create_order_object(user_id, total, payment_intent_id)
    _create_order_items_from_cart(order, cart_items)
    _decrement_product_stock(cart_items)
    _clear_user_cart(user_id)

    db.session.commit()
    db.session.refresh(order)
    
    # Send Order Confirmation Email
    user = db.session.get(User, user_id)
    if user and user.email:
        msg = Message(
            subject=f"Order Confirmation #{order.id}",
            recipients=[user.email]
        )
        msg.body = f"Thank you for your order! Your total is ${total:,.2f}."
        
        # Build Item rows
        items_html = ""
        for ci in cart_items:
            product = db.session.get(Product, ci.product_id)
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{product.name} x {ci.quantity}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">${(product.price * ci.quantity):,.2f}</td>
            </tr>
            """
            
        msg.html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <h2 style="color: #4f46e5;">Order Confirmed!</h2>
            <p>Hi {user.first_name},</p>
            <p>We've received your order <strong>#{order.id}</strong>. We'll let you know when it ships.</p>
            
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">Order Summary</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    {items_html}
                    <tr>
                        <td style="padding: 15px 10px; font-weight: bold; text-align: right;">Total</td>
                        <td style="padding: 15px 10px; font-weight: bold; text-align: right; color: #4f46e5;">${total:,.2f}</td>
                    </tr>
                </table>
            </div>
            <p style="font-size: 14px; color: #666;">Thank you for shopping with us!</p>
        </div>
        """
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send order confirmation email: {e}")
            
    return order


def get_user_orders(user_id: int, page: int = 1, per_page: int = 20) -> dict:
    """List orders for user; paginated."""
    per_page = min(per_page, 100)
    q = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    pagination = BaseService.pagination_dict(total, page, per_page)
    return {"orders": items, **pagination}


def get_by_id(order_id: int, user_id: int | None = None, admin: bool = False) -> Order:
    """Get order; if user_id set, must be owner unless admin."""
    order = db.session.get(Order, order_id)
    if not order:
        raise OrderNotFoundError(order_id)
    if not admin and user_id is not None and order.user_id != user_id:
        raise ValidationError("Not authorized to view this order", field="order_id")
    return order


def update_status(order_id: int, status: str) -> Order:
    """Admin: update order status. Valid: pending, processing, shipped, delivered, cancelled."""
    valid = {"pending", "processing", "shipped", "delivered", "cancelled"}
    if status.lower() not in valid:
        raise ValidationError(f"Invalid status; use one of {valid}", field="status")
    order = get_by_id(order_id, admin=True)
    order.status = status.lower()
    db.session.commit()
    db.session.refresh(order)
    return order


def get_all_orders_admin(page: int = 1, per_page: int = 20) -> dict:
    """Admin: list all orders."""
    per_page = min(per_page, 100)
    q = Order.query.order_by(Order.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    pagination = BaseService.pagination_dict(total, page, per_page)
    return {"orders": items, **pagination}
