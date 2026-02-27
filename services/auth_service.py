"""Auth service: register, login, logout (token blocklist), password reset."""

from typing import Tuple, Any
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.exc import IntegrityError

from database import db
from models import User
from schemas import UserCreate, UserResponse
from exceptions import DuplicateEmailError, InvalidCredentialsError, DatabaseError
from services.base_service import BaseService


# In-memory blocklist for logout (single process); use DB/Redis in production
_token_blocklist: set = set()


def register(data: UserCreate) -> Tuple[dict, str, str]:
    """Register user, return (user_dict, access_token, refresh_token)."""
    if User.query.filter_by(email=data.email.lower()).first():
        raise DuplicateEmailError(data.email)
    user = User(
        email=data.email.lower(),
        first_name=data.first_name.strip(),
        last_name=data.last_name.strip(),
        role="customer",
    )
    user.set_password(data.password)
    try:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    except IntegrityError:
        db.session.rollback()
        raise DuplicateEmailError(data.email)
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(str(e))
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return UserResponse.model_validate(user).model_dump(), access_token, refresh_token


def login(email: str, password: str) -> Tuple[dict, str, str]:
    """Authenticate user, return (user_dict, access_token, refresh_token)."""
    user = User.query.filter_by(email=email.lower()).first()
    if not user or not user.check_password(password):
        raise InvalidCredentialsError()
    if not user.is_active:
        raise InvalidCredentialsError("Account is deactivated")
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return UserResponse.model_validate(user).model_dump(), access_token, refresh_token


def logout(jti: str | None) -> None:
    """Revoke token by adding jti to blocklist (call from route with get_jwt)."""
    if jti:
        _token_blocklist.add(jti)


def is_token_revoked(jti: str) -> bool:
    """Check if token was revoked (for JWT revoke callback)."""
    return jti in _token_blocklist


# Simple in-memory reset tokens (user_id -> token); use DB/Redis in production
_reset_tokens: dict[str, int] = {}  # token -> user_id


def request_password_reset(email: str) -> None:
    """Store a reset token for the user (no email sent in minimal version)."""
    user = User.query.filter_by(email=email.lower()).first()
    if user:
        import secrets
        token = secrets.token_urlsafe(32)
        _reset_tokens[token] = user.id
    # Always return without leaking whether email exists


def confirm_password_reset(token: str, new_password: str) -> None:
    """Set new password from reset token; raise InvalidCredentialsError if invalid."""
    user_id = _reset_tokens.pop(token, None)
    if user_id is None:
        raise InvalidCredentialsError("Invalid or expired reset token")
    user = db.session.get(User, user_id)
    if not user:
        raise InvalidCredentialsError("User not found")
    user.set_password(new_password)
    db.session.commit()
