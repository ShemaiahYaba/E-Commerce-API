"""Web UI order routes: list, detail."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services import order_service
from errors.exceptions import OrderNotFoundError
from routes.web.utils import require_login

orders_web_bp = Blueprint(
    "web_orders", __name__, url_prefix="/web", template_folder="../../templates"
)


@orders_web_bp.route("/orders")
def orders_list():
    guard = require_login()
    if guard:
        return guard

    page = request.args.get("page", 1, type=int)
    try:
        result = order_service.get_user_orders(session["user_id"], page=page)
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


@orders_web_bp.route("/orders/<int:order_id>")
def order_detail(order_id: int):
    guard = require_login()
    if guard:
        return guard

    is_admin = session.get("user_role") == "admin"
    try:
        order = order_service.get_by_id(
            order_id, user_id=session["user_id"], admin=is_admin
        )
    except OrderNotFoundError:
        flash("Order not found.", "error")
        return redirect(url_for("web_orders.orders_list"))
    except Exception as e:
        flash(getattr(e, "message", "Error loading order."), "error")
        return redirect(url_for("web_orders.orders_list"))

    return render_template("orders/detail.html", order=order)
