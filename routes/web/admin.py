"""Web UI admin routes: dashboard."""

from flask import Blueprint, render_template, redirect, url_for, session, flash
from sqlalchemy import func

from config.database import db
from models import User, Order, OrderItem, Product
from services import order_service
from routes.web.utils import require_login

admin_web_bp = Blueprint(
    "web_admin", __name__, url_prefix="/web", template_folder="../../templates"
)


@admin_web_bp.route("/admin")
def admin_dashboard():
    guard = require_login()
    if guard:
        return guard

    if session.get("user_role") != "admin":
        flash("Admin access required.", "error")
        return redirect(url_for("web_products.products_list"))

    try:
        total_users = User.query.count()
        total_orders = Order.query.count()
        revenue = (
            db.session.query(func.coalesce(func.sum(Order.total), 0)).scalar() or 0
        )
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
