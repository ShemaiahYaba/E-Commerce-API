"""Web UI admin routes: dashboard, users, orders, inventory."""

from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from sqlalchemy import func

from config.database import db
from models import User, Order, OrderItem, Product
from services import order_service, user_service
from routes.web.utils import require_login, require_admin

admin_web_bp = Blueprint(
    "web_admin", __name__, url_prefix="/web/admin", template_folder="../../templates"
)


# ──────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────

@admin_web_bp.route("")
@admin_web_bp.route("/")
def admin_dashboard():
    guard = require_admin()
    if guard:
        return guard

    try:
        total_users = User.query.count()
        total_orders = Order.query.count()
        revenue = db.session.query(func.coalesce(func.sum(Order.total), 0)).scalar() or 0
        total_products = Product.query.filter(Product.is_active == True).count()
        low_stock = (
            Product.query.filter(Product.stock < 10, Product.is_active == True)
            .order_by(Product.stock.asc())
            .all()
        )
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


# ──────────────────────────────────────────────
# User management
# ──────────────────────────────────────────────

@admin_web_bp.route("/users")
def admin_users():
    guard = require_admin()
    if guard:
        return guard

    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()

    try:
        q = User.query.order_by(User.created_at.desc())
        if search:
            q = q.filter(
                db.or_(
                    User.email.ilike(f"%{search}%"),
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                )
            )
        total = q.count()
        per_page = 20
        users = q.offset((page - 1) * per_page).limit(per_page).all()
        pages = max(1, (total + per_page - 1) // per_page)
    except Exception:
        flash("Error loading users.", "error")
        users, total, pages = [], 0, 1

    return render_template(
        "admin/users.html",
        users=users,
        total=total,
        page=page,
        pages=pages,
        search_query=search,
    )


@admin_web_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
def admin_deactivate_user(user_id):
    guard = require_admin()
    if guard:
        return guard
    try:
        user_service.set_active(user_id, False)
        flash("User deactivated.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not deactivate user."), "error")
    return redirect(url_for("web_admin.admin_users"))


@admin_web_bp.route("/users/<int:user_id>/activate", methods=["POST"])
def admin_activate_user(user_id):
    guard = require_admin()
    if guard:
        return guard
    try:
        user_service.set_active(user_id, True)
        flash("User activated.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not activate user."), "error")
    return redirect(url_for("web_admin.admin_users"))


@admin_web_bp.route("/users/<int:user_id>/delete", methods=["POST"])
def admin_delete_user(user_id):
    guard = require_admin()
    if guard:
        return guard
    try:
        user_service.delete_user(user_id)
        flash("User permanently deleted.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not delete user."), "error")
    return redirect(url_for("web_admin.admin_users"))


# ──────────────────────────────────────────────
# Order management
# ──────────────────────────────────────────────

@admin_web_bp.route("/orders")
def admin_orders():
    guard = require_admin()
    if guard:
        return guard

    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status", "").strip()

    try:
        q = Order.query.order_by(Order.created_at.desc())
        if status_filter:
            q = q.filter(Order.status == status_filter)
        total = q.count()
        per_page = 20
        orders = q.offset((page - 1) * per_page).limit(per_page).all()
        pages = max(1, (total + per_page - 1) // per_page)
    except Exception:
        flash("Error loading orders.", "error")
        orders, total, pages = [], 0, 1

    statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    return render_template(
        "admin/orders.html",
        orders=orders,
        total=total,
        page=page,
        pages=pages,
        status_filter=status_filter,
        statuses=statuses,
    )


@admin_web_bp.route("/orders/<int:order_id>/status", methods=["POST"])
def admin_update_order_status(order_id):
    guard = require_admin()
    if guard:
        return guard
    new_status = request.form.get("status", "").strip()
    if not new_status:
        flash("No status provided.", "error")
        return redirect(url_for("web_admin.admin_orders"))
    try:
        order_service.update_status(order_id, new_status)
        flash(f"Order #{order_id} status updated to '{new_status}'.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not update status."), "error")
    return redirect(url_for("web_admin.admin_orders"))


@admin_web_bp.route("/orders/<int:order_id>/cancel", methods=["POST"])
def admin_cancel_order(order_id):
    guard = require_admin()
    if guard:
        return guard
    try:
        order = db.session.get(Order, order_id)
        if not order:
            flash("Order not found.", "error")
        elif order.status in ("cancelled", "delivered"):
            flash(f"Cannot cancel an order with status '{order.status}'.", "error")
        else:
            for oi in order.order_items:
                product = db.session.get(Product, oi.product_id)
                if product:
                    product.stock += oi.quantity
            order.status = "cancelled"
            db.session.commit()
            flash(f"Order #{order_id} cancelled and stock restored.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not cancel order."), "error")
    return redirect(url_for("web_admin.admin_orders"))


# ──────────────────────────────────────────────
# Inventory management
# ──────────────────────────────────────────────

@admin_web_bp.route("/inventory")
def admin_inventory():
    guard = require_admin()
    if guard:
        return guard

    search = request.args.get("q", "").strip()
    low_only = request.args.get("low_only") == "1"
    threshold = request.args.get("threshold", 10, type=int)
    page = request.args.get("page", 1, type=int)

    try:
        q = Product.query.order_by(Product.stock.asc())
        if search:
            q = q.filter(
                db.or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                )
            )
        if low_only:
            q = q.filter(Product.stock < threshold)
        total = q.count()
        per_page = 25
        products = q.offset((page - 1) * per_page).limit(per_page).all()
        pages = max(1, (total + per_page - 1) // per_page)
    except Exception:
        flash("Error loading inventory.", "error")
        products, total, pages = [], 0, 1

    return render_template(
        "admin/inventory.html",
        products=products,
        total=total,
        page=page,
        pages=pages,
        search_query=search,
        low_only=low_only,
        threshold=threshold,
    )


@admin_web_bp.route("/inventory/<int:product_id>/stock", methods=["POST"])
def admin_update_stock(product_id):
    guard = require_admin()
    if guard:
        return guard
    new_stock = request.form.get("stock", type=int)
    if new_stock is None or new_stock < 0:
        flash("Invalid stock value.", "error")
        return redirect(url_for("web_admin.admin_inventory"))
    try:
        product = db.session.get(Product, product_id)
        if not product:
            flash("Product not found.", "error")
        else:
            product.stock = new_stock
            db.session.commit()
            flash(f"Stock for '{product.name}' updated to {new_stock}.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not update stock."), "error")
    return redirect(url_for("web_admin.admin_inventory"))
