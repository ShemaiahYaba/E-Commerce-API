"""Web UI auth routes: login, register, logout, profile, passwords, health."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from pydantic import ValidationError

from services import auth_service, user_service
from schemas import UserCreate, UserUpdate
from errors.exceptions import DuplicateEmailError, InvalidCredentialsError
from routes.web.utils import require_login

auth_web_bp = Blueprint(
    "web_auth", __name__, url_prefix="/web", template_folder="../../templates"
)

# ------------------------------------------------------------------------
# Auth / Registration
# ------------------------------------------------------------------------

@auth_web_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("access_token"):
            return redirect(url_for("web_products.products_list"))
        return render_template("auth/login.html")

    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    if not email or not password:
        flash("Email and password are required.", "error")
        return redirect(url_for("web_auth.login"))

    try:
        user_dict, access_token, refresh_token = auth_service.login(email, password)
    except InvalidCredentialsError as e:
        flash(getattr(e, "message", "Invalid email or password."), "error")
        return redirect(url_for("web_auth.login"))
    except Exception:
        flash("An unexpected error occurred. Please try again.", "error")
        return redirect(url_for("web_auth.login"))

    session.update({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_email": user_dict["email"],
        "user_role": user_dict["role"],
        "user_id": user_dict["id"],
        "user_name": user_dict.get("first_name", ""),
    })
    flash(f"Welcome back, {user_dict.get('first_name', 'there')}!", "success")
    return redirect(url_for("web_products.products_list"))


@auth_web_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if session.get("access_token"):
            return redirect(url_for("web_products.products_list"))
        return render_template("auth/register.html")

    try:
        data = UserCreate.model_validate({
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
        })
    except ValidationError as exc:
        messages = "; ".join(
            f"{e['loc'][0]}: {e['msg']}" for e in exc.errors() if e.get("loc")
        )
        flash(messages or "Validation failed.", "error")
        return redirect(url_for("web_auth.register"))

    try:
        user_dict, access_token, refresh_token = auth_service.register(data)
    except DuplicateEmailError:
        flash("An account with that email already exists.", "error")
        return redirect(url_for("web_auth.register"))
    except Exception:
        flash("An unexpected error occurred. Please try again.", "error")
        return redirect(url_for("web_auth.register"))

    session.update({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_email": user_dict["email"],
        "user_role": user_dict["role"],
        "user_id": user_dict["id"],
        "user_name": user_dict.get("first_name", ""),
    })
    flash(f"Account created! Welcome, {user_dict.get('first_name', 'there')}!", "success")
    return redirect(url_for("web_products.products_list"))


@auth_web_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("web_auth.login"))


# ------------------------------------------------------------------------
# Profile Management
# ------------------------------------------------------------------------

@auth_web_bp.route("/profile", methods=["GET", "POST"])
def profile():
    guard = require_login()
    if guard:
        return guard

    user_id = session["user_id"]
    try:
        user = user_service.get_by_id(user_id)
    except Exception:
        flash("Error loading profile.", "error")
        return redirect(url_for("web_products.products_list"))

    if request.method == "GET":
        return render_template("auth/profile.html", user=user)

    # POST (update)
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()

    if not first_name or not last_name:
        flash("First and last name are required.", "error")
        return redirect(url_for("web_auth.profile"))

    update_data = UserUpdate(first_name=first_name, last_name=last_name)
    try:
        user_service.update_user(user_id, update_data)
        # update session mirror details just in case
        session["user_name"] = first_name
        flash("Profile updated successfully.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not update profile."), "error")

    return redirect(url_for("web_auth.profile"))


# ------------------------------------------------------------------------
# Passwords
# ------------------------------------------------------------------------

@auth_web_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if session.get("access_token"):
        return redirect(url_for("web_auth.profile"))

    if request.method == "GET":
        return render_template("auth/forgot_password.html")

    email = request.form.get("email", "").strip().lower()
    if not email:
        flash("Email is required.", "error")
        return redirect(url_for("web_auth.forgot_password"))

    # Security: always show same success message so we don't leak user existence
    try:
        auth_service.request_password_reset(email)
    except Exception:
        pass  # ignore errors like UserNotFound

    flash("If your email is in our system, a password reset link has been sent.", "success")
    return redirect(url_for("web_auth.login"))


@auth_web_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if session.get("access_token"):
        return redirect(url_for("web_auth.profile"))

    if request.method == "GET":
        token = request.args.get("token", "")
        if not token:
            flash("Invalid or missing reset token.", "error")
            return redirect(url_for("web_auth.login"))
        return render_template("auth/reset_password.html", token=token)

    token = request.form.get("token", "")
    new_password = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")

    if not token or not new_password:
        flash("Token and new password required.", "error")
        return redirect(url_for("web_auth.reset_password", token=token))
    
    if new_password != confirm:
        flash("Passwords do not match.", "error")
        return redirect(url_for("web_auth.reset_password", token=token))

    try:
        auth_service.confirm_password_reset(token, new_password)
        flash("Password reset successful. Please log in.", "success")
        return redirect(url_for("web_auth.login"))
    except Exception as e:
        flash(getattr(e, "message", "Reset failed or token expired."), "error")
        return redirect(url_for("web_auth.reset_password", token=token))


# ------------------------------------------------------------------------
# Health Route
# ------------------------------------------------------------------------

@auth_web_bp.route("/health")
def health_ui():
    """Web UI for health check (no auth required)."""
    from time import time
    from database import db
    import sys

    # Attempt a quick DB check
    db_ok = False
    try:
        db.session.execute(db.text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    uptime = time() - app_start_time if 'app_start_time' in globals() else 0
    py_version = sys.version.split(' ')[0]

    return render_template(
        "health.html", 
        db_ok=db_ok, 
        uptime=uptime, 
        py_version=py_version
    )

# Record start time for uptime tracking
from time import time
app_start_time = time()
