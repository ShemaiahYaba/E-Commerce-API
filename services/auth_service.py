"""Auth service: register, login, logout (token blocklist), password reset."""

from typing import Tuple, Any
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.exc import IntegrityError

from database import db
from models import User
from schemas import UserCreate, UserResponse
from exceptions import DuplicateEmailError, InvalidCredentialsError, DatabaseError
from services.base_service import BaseService
from config.mail import mail
from flask_mail import Message
from flask import current_app, url_for


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
    """Store a reset token for the user and send an email via Flask-Mail."""
    user = User.query.filter_by(email=email.lower()).first()
    if user:
        import secrets
        token = secrets.token_urlsafe(32)
        _reset_tokens[token] = user.id
        
        # Build the reset URL
        from flask import request
        # fallback to a default host if request is not available
        host_url = request.host_url if request else "http://localhost:5000/"
        reset_url = f"{host_url.rstrip('/')}/web/reset-password?token={token}"
        
        # We'll use the mail client directly
        msg = Message(
            subject="Password Reset Request",
            recipients=[user.email]
        )
        msg.body = f"Click the link to reset your password: {reset_url}"
        msg.html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Reset your Password</h2>
            <p>Hi {user.first_name},</p>
            <p>We received a request to reset your password for your ShopAPI account.</p>
            <p>
                <a href="{reset_url}" style="display: inline-block; padding: 10px 20px; background-color: #4f46e5; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Reset Password
                </a>
            </p>
            <p style="color: #666; font-size: 14px; margin-top: 30px;">
                If you didn't request this, you can safely ignore this email.
            </p>
        </div>
        """
        
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send reset email: {e}")
            
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
