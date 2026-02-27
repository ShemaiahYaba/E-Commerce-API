"""Product and ProductImage models."""

from datetime import datetime

from database import db


class Product(db.Model):
    """Product in catalog; belongs to a category."""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False, index=True)
    stock = db.Column(db.Integer, nullable=False, default=0, index=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    order_items = db.relationship("OrderItem", backref="product", lazy="dynamic")
    cart_items = db.relationship("CartItem", backref="product", lazy="dynamic")
    reviews = db.relationship(
        "Review", backref="product", lazy="dynamic", cascade="all, delete-orphan"
    )
    wishlist_items = db.relationship(
        "WishlistItem", backref="product", lazy="dynamic", cascade="all, delete-orphan"
    )
    images = db.relationship(
        "ProductImage", backref="product", lazy="dynamic", cascade="all, delete-orphan"
    )


class ProductImage(db.Model):
    """Product image; url or path and sort order."""

    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False, index=True
    )
    url = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
