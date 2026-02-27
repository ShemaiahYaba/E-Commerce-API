"""Reusable model mixins."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

def timestamp_columns(db: SQLAlchemy) -> dict:
    """Return created_at and updated_at column definitions."""
    return {
        "created_at": db.Column(db.DateTime, default=datetime.utcnow, nullable=False),
        "updated_at": db.Column(
            db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
        ),
    }
