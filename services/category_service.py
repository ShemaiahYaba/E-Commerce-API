"""Category service: CRUD and list."""

from typing import List
from database import db
from models import Category
from schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from exceptions import CategoryNotFoundError
from services.base_service import BaseService


def get_all() -> List[Category]:
    """Return all categories."""
    return Category.query.order_by(Category.name).all()


def get_by_id(category_id: int) -> Category:
    """Get category by id; raise CategoryNotFoundError if missing."""
    cat = db.session.get(Category, category_id)
    if not cat:
        raise CategoryNotFoundError(category_id)
    return cat


def create(data: CategoryCreate) -> Category:
    """Create category."""
    cat = Category(name=data.name.strip(), parent_id=data.parent_id)
    db.session.add(cat)
    db.session.commit()
    db.session.refresh(cat)
    return cat


def update(category_id: int, data: CategoryUpdate) -> Category:
    """Update category."""
    cat = get_by_id(category_id)
    payload = data.model_dump(exclude_unset=True)
    for k, v in payload.items():
        setattr(cat, k, v)
    db.session.commit()
    db.session.refresh(cat)
    return cat


def delete(category_id: int) -> None:
    """Delete category."""
    cat = get_by_id(category_id)
    db.session.delete(cat)
    db.session.commit()
