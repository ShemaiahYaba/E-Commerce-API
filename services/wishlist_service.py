"""Wishlist service: add, list, remove."""

from database import db
from models import WishlistItem, Product
from exceptions import ProductNotFoundError
from services.product_service import get_by_id as get_product


def get_wishlist(user_id: int) -> list:
    """Return list of wishlist items (with product) for user."""
    return WishlistItem.query.filter_by(user_id=user_id).all()


def add(user_id: int, product_id: int) -> WishlistItem | None:
    """Add product to wishlist; return existing item if already in wishlist."""
    get_product(product_id)
    existing = WishlistItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        return existing
    item = WishlistItem(user_id=user_id, product_id=product_id)
    db.session.add(item)
    db.session.commit()
    db.session.refresh(item)
    return item


def remove(user_id: int, product_id: int) -> bool:
    """Remove product from wishlist; return True if found and removed."""
    item = WishlistItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not item:
        return False
    db.session.delete(item)
    db.session.commit()
    return True
