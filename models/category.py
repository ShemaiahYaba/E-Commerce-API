"""Category model; supports optional parent for subcategories."""

from datetime import datetime

from database import db


class Category(db.Model):
    """Product category; optional parent_id for subcategories."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    parent = db.relationship("Category", remote_side=[id], backref="children")
    products = db.relationship("Product", backref="category", lazy="select")
