"""Order service: create from cart, list, get, admin status update, payment_intent simulation."""

import uuid
from decimal import Decimal
from database import db
from models import Order, OrderItem, CartItem, Product
from exceptions import OrderNotFoundError, ValidationError
from services.base_service import BaseService


def create_order(user_id: int) -> Order:
    """Create order from cart; decrement stock, clear cart. Simulate payment_intent_id. Optionally trigger email."""
    items = CartItem.query.filter_by(user_id=user_id).all()
    if not items:
        raise ValidationError("Cart is empty", field="cart")
    total = Decimal("0")
    order_items_to_create = []
    for ci in items:
        product = db.session.get(Product, ci.product_id)
        if not product or product.stock < ci.quantity:
            raise ValidationError(
                f"Insufficient stock for product {ci.product_id}",
                field="stock",
            )
        total += product.price * ci.quantity
        order_items_to_create.append((product, ci.quantity))
    payment_intent_id = f"pi_sim_{uuid.uuid4().hex[:24]}"
    order = Order(
        user_id=user_id,
        status="pending",
        total=total,
        payment_intent_id=payment_intent_id,
    )
    db.session.add(order)
    db.session.flush()
    for product, qty in order_items_to_create:
        oi = OrderItem(order_id=order.id, product_id=product.id, quantity=qty, price=product.price)
        db.session.add(oi)
        product.stock -= qty
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    db.session.refresh(order)
    # Stub: order confirmation email (OM-06)
    # send_order_confirmation_email(user_id, order)  # implement with SMTP or mock
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
