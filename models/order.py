"""Order and OrderItem models."""

from datetime import datetime

from database import db


class Order(db.Model):
    """Order header; status and optional payment_intent_id (simulated)."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default="pending", index=True)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    payment_intent_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    order_items = db.relationship(
        "OrderItem", backref="order", lazy="dynamic", cascade="all, delete-orphan"
    )


class OrderItem(db.Model):
    """Order line: product snapshot (quantity, price at time of order)."""

    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False, index=True
    )
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
