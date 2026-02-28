"""Webdocs UI: Jinja + Tailwind pages for visual API testing.

All routes call the service layer directly; no internal HTTP hops.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from pydantic import ValidationError

from services import auth_service, product_service, category_service, cart_service, order_service
from schemas import UserCreate
from exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    ProductNotFoundError,
    OrderNotFoundError,
)

webdocs_bp = Blueprint(
    "webdocs", __name__, url_prefix="/web", template_folder="../templates"
)


def _require_login():
    """Return redirect to login if user has no session token, else None."""
    if not session.get("access_token"):
        flash("Please log in to continue.", "error")
        return redirect(url_for("webdocs.login"))
    return None


# ---------------------------------------------------------------------------
# DOCS LANDING
# ---------------------------------------------------------------------------


@webdocs_bp.route("/docs")
def index():
    """Webdocs landing: links to Swagger and endpoint list."""
    return render_template("webdocs/index.html")


# ---------------------------------------------------------------------------
# AUTH ROUTES
# ---------------------------------------------------------------------------


@webdocs_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page and handler."""
    if request.method == "GET":
        if session.get("access_token"):
            return redirect(url_for("webdocs.products_list"))
        return render_template("auth/login.html")

    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    if not email or not password:
        flash("Email and password are required.", "error")
        return redirect(url_for("webdocs.login"))

    try:
        user_dict, access_token, refresh_token = auth_service.login(email, password)
    except InvalidCredentialsError as e:
        flash(getattr(e, "message", "Invalid email or password."), "error")
        return redirect(url_for("webdocs.login"))
    except Exception:
        flash("An unexpected error occurred. Please try again.", "error")
        return redirect(url_for("webdocs.login"))

    session["access_token"] = access_token
    session["refresh_token"] = refresh_token
    session["user_email"] = user_dict["email"]
    session["user_role"] = user_dict["role"]
    session["user_id"] = user_dict["id"]
    session["user_name"] = user_dict.get("first_name", "")

    flash(f"Welcome back, {user_dict.get('first_name', 'there')}!", "success")
    return redirect(url_for("webdocs.products_list"))


@webdocs_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register page and handler."""
    if request.method == "GET":
        if session.get("access_token"):
            return redirect(url_for("webdocs.products_list"))
        return render_template("auth/register.html")

    try:
        data = UserCreate.model_validate(
            {
                "email": request.form.get("email"),
                "password": request.form.get("password"),
                "first_name": request.form.get("first_name"),
                "last_name": request.form.get("last_name"),
            }
        )
    except ValidationError as exc:
        messages = "; ".join(
            f"{e['loc'][0]}: {e['msg']}" for e in exc.errors() if e.get("loc")
        )
        flash(messages or "Validation failed.", "error")
        return redirect(url_for("webdocs.register"))

    try:
        user_dict, access_token, refresh_token = auth_service.register(data)
    except DuplicateEmailError:
        flash("An account with that email already exists.", "error")
        return redirect(url_for("webdocs.register"))
    except Exception:
        flash("An unexpected error occurred. Please try again.", "error")
        return redirect(url_for("webdocs.register"))

    session["access_token"] = access_token
    session["refresh_token"] = refresh_token
    session["user_email"] = user_dict["email"]
    session["user_role"] = user_dict["role"]
    session["user_id"] = user_dict["id"]
    session["user_name"] = user_dict.get("first_name", "")

    flash(f"Account created! Welcome, {user_dict.get('first_name', 'there')}!", "success")
    return redirect(url_for("webdocs.products_list"))


@webdocs_bp.route("/logout")
def logout():
    """Logout: clear session."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("webdocs.login"))


# ---------------------------------------------------------------------------
# PRODUCT ROUTES
# ---------------------------------------------------------------------------


@webdocs_bp.route("/products")
def products_list():
    """Product listing with search, category filter and pagination."""
    guard = _require_login()
    if guard:
        return guard

    search = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    page = request.args.get("page", 1, type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    in_stock = request.args.get("in_stock") == "1"

    try:
        result = product_service.get_all_paginated(
            page=page,
            per_page=12,
            search=search or None,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock,
        )
        categories = category_service.get_all()
    except Exception:
        flash("Error loading products.", "error")
        result = {"products": [], "total": 0, "page": 1, "pages": 1}
        categories = []

    return render_template(
        "products/list.html",
        products=result["products"],
        total=result["total"],
        page=result["page"],
        pages=result["pages"],
        categories=categories,
        current_category=category_id,
        search_query=search,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
    )


@webdocs_bp.route("/products/<int:product_id>")
def product_detail(product_id: int):
    """Product detail page."""
    guard = _require_login()
    if guard:
        return guard

    try:
        product = product_service.get_by_id(product_id)
    except ProductNotFoundError:
        flash("Product not found.", "error")
        return redirect(url_for("webdocs.products_list"))
    except Exception:
        flash("Error loading product.", "error")
        return redirect(url_for("webdocs.products_list"))

    return render_template("products/detail.html", product=product)


# ---------------------------------------------------------------------------
# CART ROUTES
# ---------------------------------------------------------------------------


@webdocs_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def cart_add(product_id: int):
    """Add item to cart."""
    guard = _require_login()
    if guard:
        return guard

    user_id = session["user_id"]
    quantity = request.form.get("quantity", 1, type=int)

    try:
        cart_service.add_item(user_id, product_id, quantity)
        flash("Item added to cart!", "success")
    except ProductNotFoundError:
        flash("Product not found.", "error")
    except Exception as e:
        flash(getattr(e, "message", "Could not add to cart."), "error")

    return redirect(request.referrer or url_for("webdocs.products_list"))


@webdocs_bp.route("/cart")
def cart_view():
    """Full cart view."""
    guard = _require_login()
    if guard:
        return guard

    user_id = session["user_id"]
    try:
        cart = cart_service.get_cart(user_id)
    except Exception:
        flash("Error loading cart.", "error")
        cart = {"items": [], "total": 0}

    return render_template("cart/view.html", items=cart["items"], total=cart["total"])


@webdocs_bp.route("/cart/update/<int:item_id>", methods=["POST"])
def cart_update(item_id: int):
    """Update cart item quantity."""
    guard = _require_login()
    if guard:
        return guard

    user_id = session["user_id"]
    quantity = request.form.get("quantity", 1, type=int)

    try:
        cart_service.update_quantity(user_id, item_id, quantity)
    except Exception as e:
        flash(getattr(e, "message", "Could not update cart."), "error")

    return redirect(url_for("webdocs.cart_view"))


@webdocs_bp.route("/cart/remove/<int:item_id>", methods=["POST"])
def cart_remove(item_id: int):
    """Remove cart item."""
    guard = _require_login()
    if guard:
        return guard

    cart_service.remove_item(session["user_id"], item_id)
    flash("Item removed from cart.", "success")
    return redirect(url_for("webdocs.cart_view"))


@webdocs_bp.route("/cart/checkout", methods=["POST"])
def cart_checkout():
    """Create order from cart."""
    guard = _require_login()
    if guard:
        return guard

    user_id = session["user_id"]
    try:
        order = order_service.create_order(user_id)
        flash(f"Order #{order.id} placed successfully! 🎉", "success")
        return redirect(url_for("webdocs.order_detail", order_id=order.id))
    except Exception as e:
        flash(getattr(e, "message", "Could not place order."), "error")
        return redirect(url_for("webdocs.cart_view"))


# ---------------------------------------------------------------------------
# ORDER ROUTES
# ---------------------------------------------------------------------------


@webdocs_bp.route("/orders")
def orders_list():
    """Order list for current user."""
    guard = _require_login()
    if guard:
        return guard

    page = request.args.get("page", 1, type=int)
    user_id = session["user_id"]

    try:
        result = order_service.get_user_orders(user_id, page=page)
    except Exception:
        flash("Error loading orders.", "error")
        result = {"orders": [], "total": 0, "page": 1, "pages": 1}

    return render_template(
        "orders/list.html",
        orders=result["orders"],
        total=result["total"],
        page=result["page"],
        pages=result["pages"],
    )


@webdocs_bp.route("/orders/<int:order_id>")
def order_detail(order_id: int):
    """Order detail for current user."""
    guard = _require_login()
    if guard:
        return guard

    user_id = session["user_id"]
    is_admin = session.get("user_role") == "admin"

    try:
        order = order_service.get_by_id(order_id, user_id=user_id, admin=is_admin)
    except OrderNotFoundError:
        flash("Order not found.", "error")
        return redirect(url_for("webdocs.orders_list"))
    except Exception as e:
        flash(getattr(e, "message", "Error loading order."), "error")
        return redirect(url_for("webdocs.orders_list"))

    return render_template("orders/detail.html", order=order)


# ---------------------------------------------------------------------------
# ADMIN ROUTES
# ---------------------------------------------------------------------------


@webdocs_bp.route("/admin")
def admin_dashboard():
    """Admin dashboard (admin only)."""
    guard = _require_login()
    if guard:
        return guard

    if session.get("user_role") != "admin":
        flash("Admin access required.", "error")
        return redirect(url_for("webdocs.products_list"))

    from database import db
    from models import User, Order, OrderItem, Product
    from sqlalchemy import func

    try:
        total_users = User.query.count()
        total_orders = Order.query.count()
        revenue = db.session.query(func.coalesce(func.sum(Order.total), 0)).scalar() or 0
        total_products = Product.query.filter(Product.is_active == True).count()
        low_stock = Product.query.filter(Product.stock < 10, Product.is_active == True).order_by(Product.stock.asc()).all()
        orders_result = order_service.get_all_orders_admin(page=1, per_page=8)
        stats = {
            "total_users": total_users,
            "total_orders": total_orders,
            "revenue": float(revenue),
            "total_products": total_products,
        }
    except Exception:
        flash("Error loading admin data.", "error")
        stats = {"total_users": 0, "total_orders": 0, "revenue": 0, "total_products": 0}
        low_stock = []
        orders_result = {"orders": []}

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        low_stock=low_stock,
        recent_orders=orders_result["orders"],
    )
