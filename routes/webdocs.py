"""Webdocs UI: Jinja + Tailwind pages for visual API testing."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests
from http import HTTPStatus

webdocs_bp = Blueprint("webdocs", __name__, url_prefix="/web", template_folder="../templates")


def _api_base():
    """API base URL from current request (works on any host/port)."""
    return request.host_url.rstrip("/") + "/api/v1"


@webdocs_bp.route("/docs")
def index():
    """Webdocs landing: links to Swagger and endpoint list."""
    return render_template("webdocs/index.html")


# ---------------------------------------------------------------------------
# AUTHENTICATION ROUTES
# ---------------------------------------------------------------------------

@webdocs_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page and handler."""
    if request.method == "GET":
        if session.get("access_token"):
            return redirect(url_for("webdocs.products_list"))
        return render_template("auth/login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    try:
        response = requests.post(
            f"{_api_base()}/auth/login",
            json={"email": email, "password": password},
            timeout=5,
        )

        if response.status_code == HTTPStatus.OK:
            data = response.json()["data"]
            session["access_token"] = data["access_token"]
            session["user_email"] = data["user"]["email"]
            session["user_role"] = data["user"]["role"]
            session["user_id"] = data["user"]["id"]
            flash("Login successful!", "success")
            return redirect(url_for("webdocs.products_list"))
        error_msg = response.json().get("message", "Login failed")
        flash(error_msg, "error")
        return redirect(url_for("webdocs.login"))
    except requests.exceptions.RequestException as e:
        flash(f"Connection error: {str(e)}", "error")
        return redirect(url_for("webdocs.login"))


@webdocs_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register page and handler."""
    if request.method == "GET":
        if session.get("access_token"):
            return redirect(url_for("webdocs.products_list"))
        return render_template("auth/register.html")

    email = request.form.get("email")
    password = request.form.get("password")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    try:
        response = requests.post(
            f"{_api_base()}/auth/register",
            json={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
            },
            timeout=5,
        )

        if response.status_code == HTTPStatus.CREATED:
            data = response.json()["data"]
            session["access_token"] = data["access_token"]
            session["user_email"] = data["user"]["email"]
            session["user_role"] = data["user"]["role"]
            session["user_id"] = data["user"]["id"]
            flash("Account created successfully!", "success")
            return redirect(url_for("webdocs.products_list"))
        error_msg = response.json().get("message", "Registration failed")
        flash(error_msg, "error")
        return redirect(url_for("webdocs.register"))
    except requests.exceptions.RequestException as e:
        flash(f"Connection error: {str(e)}", "error")
        return redirect(url_for("webdocs.register"))


@webdocs_bp.route("/logout")
def logout():
    """Logout: clear session and redirect to login."""
    if session.get("access_token"):
        try:
            requests.post(
                f"{_api_base()}/auth/logout",
                headers={"Authorization": f"Bearer {session['access_token']}"},
                timeout=5,
            )
        except requests.exceptions.RequestException:
            pass
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("webdocs.login"))


# ---------------------------------------------------------------------------
# PLACEHOLDER FOR PRODUCTS (build next phase)
# ---------------------------------------------------------------------------

@webdocs_bp.route("/products")
def products_list():
    """Product listing page (placeholder for now)."""
    if not session.get("access_token"):
        flash("Please login first", "error")
        return redirect(url_for("webdocs.login"))
    return render_template("webdocs/products_placeholder.html")
