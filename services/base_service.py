"""Base service helpers (safe commit, pagination)."""

from typing import Any
from database import db
from sqlalchemy.exc import SQLAlchemyError
from exceptions import DatabaseError


class BaseService:
    """Shared DB helpers for services."""

    @staticmethod
    def safe_commit(error_message: str = "Failed to commit changes") -> None:
        """Commit and rollback on error."""
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"{error_message}: {str(e)}")

    @staticmethod
    def pagination_dict(total: int, page: int, per_page: int) -> dict[str, Any]:
        """Return pagination metadata."""
        pages = (total + per_page - 1) // per_page if per_page else 0
        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1,
        }
