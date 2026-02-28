"""Order service: create from cart, list, get, admin status update, payment_intent simulation."""

import uuid
from decimal import Decimal
from typing import List

from database import db
from models import Order, OrderItem, CartItem, Product
from exceptions import OrderNotFoundError, ValidationError
from validators import OrderValidator
from services.base_service import BaseService


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


def create_order(user_id: int) -> Order:
    """Create order from cart; decrement stock, clear cart. Simulate payment_intent_id."""
    cart_items = _get_cart_items(user_id)
    _verify_cart_stock(cart_items)
    total = _calculate_cart_total(cart_items)
    payment_intent_id = _generate_payment_intent_id()

    order = _create_order_object(user_id, total, payment_intent_id)
    _create_order_items_from_cart(order, cart_items)
    _decrement_product_stock(cart_items)
    _clear_user_cart(user_id)

    db.session.commit()
    db.session.refresh(order)
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
