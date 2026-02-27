"""User service: get/update profile, admin list/deactivate."""

from typing import List, Optional
from database import db
from models import User
from schemas import UserUpdate, UserResponse
from exceptions import UserNotFoundError
from services.base_service import BaseService


def get_by_id(user_id: int) -> User:
    """Get user by id; raise UserNotFoundError if missing."""
    user = db.session.get(User, user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return user


def update_profile(user_id: int, data: UserUpdate) -> dict:
    """Update user profile; return user dict."""
    user = get_by_id(user_id)
    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(user, key, value)
    db.session.commit()
    db.session.refresh(user)
    return UserResponse.model_validate(user).model_dump()


def get_all_paginated(page: int = 1, per_page: int = 20) -> dict:
    """List users (admin); return items and pagination."""
    per_page = min(per_page, 100)
    q = User.query.order_by(User.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    pagination = BaseService.pagination_dict(total, page, per_page)
    return {
        "users": [UserResponse.model_validate(u).model_dump() for u in items],
        **pagination,
    }


def set_active(user_id: int, is_active: bool) -> None:
    """Deactivate/activate user (admin)."""
    user = get_by_id(user_id)
    user.is_active = is_active
    db.session.commit()
