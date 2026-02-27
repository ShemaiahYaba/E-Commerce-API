"""Cart service: add, update, remove, get, clear. Validates stock."""

from decimal import Decimal
from database import db
from models import CartItem, Product
from exceptions import ProductNotFoundError, ValidationError
from services.base_service import BaseService


def get_cart(user_id: int) -> dict:
    """Return cart items and total for user."""
    items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum(
        (item.product.price * item.quantity) for item in items
    )
    return {"items": items, "total": total}


def add_item(user_id: int, product_id: int, quantity: int = 1) -> CartItem:
    """Add or update quantity; validate stock. Raise ProductNotFoundError or ValidationError."""
    product = db.session.get(Product, product_id)
    if not product:
        raise ProductNotFoundError(product_id)
    if product.stock < quantity:
        raise ValidationError(
            f"Insufficient stock: available {product.stock}, requested {quantity}",
            field="quantity",
        )
    existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        new_qty = existing.quantity + quantity
        if product.stock < new_qty:
            raise ValidationError(
                f"Insufficient stock: available {product.stock}, requested {new_qty}",
                field="quantity",
            )
        existing.quantity = new_qty
        db.session.commit()
        db.session.refresh(existing)
        return existing
    item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(item)
    db.session.commit()
    db.session.refresh(item)
    return item


def update_quantity(user_id: int, cart_item_id: int, quantity: int) -> CartItem | None:
    """Update cart item quantity; if 0, remove. Return item or None if removed."""
    item = CartItem.query.filter_by(id=cart_item_id, user_id=user_id).first()
    if not item:
        return None
    if quantity <= 0:
        db.session.delete(item)
        db.session.commit()
        return None
    if item.product.stock < quantity:
        raise ValidationError(
            f"Insufficient stock: available {item.product.stock}, requested {quantity}",
            field="quantity",
        )
    item.quantity = quantity
    db.session.commit()
    db.session.refresh(item)
    return item


def remove_item(user_id: int, cart_item_id: int) -> bool:
    """Remove cart item; return True if found and removed."""
    item = CartItem.query.filter_by(id=cart_item_id, user_id=user_id).first()
    if not item:
        return False
    db.session.delete(item)
    db.session.commit()
    return True


def clear_cart(user_id: int) -> None:
    """Remove all cart items for user."""
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
