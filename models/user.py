"""User model."""

from datetime import datetime

from database import db


class User(db.Model):
    """User account; role admin or customer."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer", index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    orders = db.relationship("Order", backref="user", lazy="select", cascade="all, delete-orphan")
    cart_items = db.relationship(
        "CartItem", backref="user", lazy="select", cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        "Review", backref="user", lazy="select", cascade="all, delete-orphan"
    )
    wishlist_items = db.relationship(
        "WishlistItem", backref="user", lazy="select", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """Hash and set password."""
        from utils.security import hash_password
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        from utils.security import check_password
        return check_password(password, self.password_hash)
