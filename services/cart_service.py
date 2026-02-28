"""Cart service: add, update, remove, get, clear. Validates stock."""

from decimal import Decimal
from database import db
from models import CartItem, Product
from exceptions import ProductNotFoundError
from validators import CartValidator
from services.base_service import BaseService


def _verify_product_exists(product_id: int) -> Product:
    """Return product by id; raise ProductNotFoundError if missing."""
    product = db.session.get(Product, product_id)
    if not product:
        raise ProductNotFoundError(product_id)
    return product


def get_cart(user_id: int) -> dict:
    """Return cart items and total for user."""
    items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum((item.product.price * item.quantity) for item in items)
    return {"items": items, "total": total}


def add_item(user_id: int, product_id: int, quantity: int = 1) -> CartItem:
    """Add or update quantity; validate stock. Raise ProductNotFoundError or ValidationError."""
    product = _verify_product_exists(product_id)
    CartValidator.validate_quantity(quantity, product.stock)
    existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        new_qty = existing.quantity + quantity
        CartValidator.validate_quantity(new_qty, product.stock)
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
    CartValidator.validate_quantity(quantity, item.product.stock)
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
