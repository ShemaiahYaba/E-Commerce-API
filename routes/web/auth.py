"""Web UI auth routes: login, register, logout."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pydantic import ValidationError

from services import auth_service
from schemas import UserCreate
from errors.exceptions import DuplicateEmailError, InvalidCredentialsError

auth_web_bp = Blueprint(
    "web_auth", __name__, url_prefix="/web", template_folder="../../templates"
)


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
