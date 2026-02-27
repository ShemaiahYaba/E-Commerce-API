"""Auth routes: register, login, logout, password reset."""

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from http import HTTPStatus
from pydantic import ValidationError

from schemas import UserCreate, LoginRequest
from services import auth_service
from utils.responses import success_response, error_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user. Returns user and tokens."""
    try:
        data = UserCreate.model_validate(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    try:
        user_dict, access_token, refresh_token = auth_service.register(data)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "user": user_dict,
        },
        status=HTTPStatus.CREATED,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login with email and password. Returns tokens and user."""
    try:
        body = LoginRequest.model_validate(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    try:
        user_dict, access_token, refresh_token = auth_service.login(
            body.email, body.password
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "user": user_dict,
        },
        status=HTTPStatus.OK,
    )


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Invalidate current token."""
    jwt_data = get_jwt()
    jti = jwt_data.get("jti")
    auth_service.logout(jti)
    return success_response(data={"message": "Logged out"}, status=HTTPStatus.OK)


@auth_bp.route("/password-reset", methods=["POST"])
def password_reset_request():
    """Request password reset (sends token if email exists; no leak)."""
    body = request.get_json() or {}
    email = (body.get("email") or "").strip().lower()
    if not email:
        return error_response("Email required", HTTPStatus.BAD_REQUEST)
    auth_service.request_password_reset(email)
    return success_response(data={"message": "If the email exists, a reset link was sent."})

@auth_bp.route("/password-reset/confirm", methods=["POST"])
def password_reset_confirm():
    """Confirm password reset with token and new password."""
    body = request.get_json() or {}
    token = body.get("token")
    new_password = body.get("new_password")
    if not token or not new_password:
        return error_response("token and new_password required", HTTPStatus.BAD_REQUEST)
    try:
        auth_service.confirm_password_reset(token, new_password)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(data={"message": "Password updated."})

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Return current user from JWT (alias for GET /users/me)."""
    from services.user_service import get_by_id
    from schemas import UserResponse
    user_id = get_jwt_identity()
    user = get_by_id(int(user_id))
    return success_response(data=UserResponse.model_validate(user).model_dump())
