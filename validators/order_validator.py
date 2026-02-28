"""Order business rules: cart and stock validation."""

from typing import List

from database import db
from models import CartItem, Product

from validators.base_validator import BaseValidator


class OrderValidator(BaseValidator):
    """Validate order creation (cart not empty, stock sufficient)."""

    @staticmethod
    def validate_cart_not_empty(cart_items: List[CartItem]) -> None:
        """Raise ValidationError if cart has no items."""
        if not cart_items:
            BaseValidator._raise("Cart is empty", field="cart")

    @staticmethod
    def validate_cart_stock(cart_items: List[CartItem]) -> None:
        """Raise ValidationError if any cart item exceeds product stock."""
        for ci in cart_items:
            product = db.session.get(Product, ci.product_id)
            if not product:
                BaseValidator._raise(f"Product {ci.product_id} not found", field="product_id")
            if product.stock < ci.quantity:
                BaseValidator._raise(
                    f"Insufficient stock for product {ci.product_id}",
                    field="stock",
                )
