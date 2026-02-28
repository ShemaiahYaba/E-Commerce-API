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


# ──────────────────────────────────────────────
# Product Management
# ──────────────────────────────────────────────

@admin_web_bp.route("/products")
def admin_products():
    guard = require_admin()
    if guard:
        return guard

    search = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    page = request.args.get("page", 1, type=int)

    from services import product_service, category_service
    try:
        result = product_service.get_all_paginated(
            page=page, per_page=20, search=search or None, category_id=category_id
        )
        products = result["products"]
        total = result["total"]
        pages = result["pages"]
        categories = category_service.get_all()
    except Exception:
        flash("Error loading products.", "error")
        products, total, pages, categories = [], 0, 1, []

    return render_template(
        "admin/products.html",
        products=products,
        total=total,
        page=page,
        pages=pages,
        categories=categories,
        current_category=category_id,
        search_query=search,
    )


@admin_web_bp.route("/products/new", methods=["GET", "POST"])
def admin_product_new():
    guard = require_admin()
    if guard:
        return guard

    from services import product_service, category_service
    from schemas import ProductCreate
    from pydantic import ValidationError

    if request.method == "GET":
        try:
            categories = category_service.get_all()
        except Exception:
            categories = []
            flash("Could not load categories.", "error")
        return render_template("admin/product_form.html", product=None, categories=categories)

    try:
        data = ProductCreate.model_validate({
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "price": request.form.get("price"),
            "stock": request.form.get("stock"),
            "sku": request.form.get("sku"),
            "category_id": request.form.get("category_id"),
            "is_active": request.form.get("is_active") == "1",
        })
        product_service.create(data)
        flash("Product created successfully.", "success")
        return redirect(url_for("web_admin.admin_products"))
    except ValidationError as exc:
        msg = "; ".join(f"{e['loc'][0]}: {e['msg']}" for e in exc.errors() if e.get("loc"))
        flash(msg or "Validation failed.", "error")
    except Exception as e:
        flash(getattr(e, "message", "Could not create product."), "error")

    # Get categories so we can re-render form
    try:
        categories = category_service.get_all()
    except Exception:
        categories = []
    # pass form data back
    return render_template("admin/product_form.html", product=None, categories=categories, form_data=request.form)


@admin_web_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def admin_product_edit(product_id: int):
    guard = require_admin()
    if guard:
        return guard

    from services import product_service, category_service
    from schemas import ProductUpdate
    from pydantic import ValidationError

    try:
        product = product_service.get_by_id(product_id)
        categories = category_service.get_all()
    except Exception:
        flash("Could not load product or categories.", "error")
        return redirect(url_for("web_admin.admin_products"))

    if request.method == "GET":
        return render_template("admin/product_form.html", product=product, categories=categories)

    try:
        update_data = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "price": request.form.get("price") or None,
            "stock": request.form.get("stock") or None,
            "sku": request.form.get("sku"),
            "category_id": request.form.get("category_id") or None,
            "is_active": request.form.get("is_active") == "1",
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        data = ProductUpdate.model_validate(update_data)
        product_service.update(product_id, data)
        flash("Product updated successfully.", "success")
        return redirect(url_for("web_admin.admin_products"))
    except ValidationError as exc:
        msg = "; ".join(f"{e['loc'][0]}: {e['msg']}" for e in exc.errors() if e.get("loc"))
        flash(msg or "Validation failed.", "error")
    except Exception as e:
        flash(getattr(e, "message", "Could not update product."), "error")

    return render_template("admin/product_form.html", product=product, categories=categories)


@admin_web_bp.route("/products/<int:product_id>/delete", methods=["POST"])
def admin_product_delete(product_id: int):
    guard = require_admin()
    if guard:
        return guard
    from services import product_service
    try:
        product_service.delete(product_id)
        flash("Product deleted.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not delete product."), "error")
    return redirect(url_for("web_admin.admin_products"))


@admin_web_bp.route("/products/<int:product_id>/image", methods=["POST"])
def admin_product_image(product_id: int):
    guard = require_admin()
    if guard:
        return guard
    from services import product_service
    
    # In a real app we'd save the file to S3/disk. Here we just take the URL.
    image_url = request.form.get("image_url", "").strip()
    if not image_url:
        flash("Image URL is required.", "error")
        return redirect(url_for("web_admin.admin_product_edit", product_id=product_id))

    try:
        product_service.add_image(product_id, image_url)
        flash("Image added successfully.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not add image."), "error")

    return redirect(url_for("web_admin.admin_product_edit", product_id=product_id))


# ──────────────────────────────────────────────
# Category Management
# ──────────────────────────────────────────────

@admin_web_bp.route("/categories")
def admin_categories():
    guard = require_admin()
    if guard:
        return guard
    from services import category_service
    try:
        categories = category_service.get_all()
    except Exception:
        flash("Error loading categories.", "error")
        categories = []

    return render_template("admin/categories.html", categories=categories)


@admin_web_bp.route("/categories/new", methods=["POST"])
def admin_category_new():
    guard = require_admin()
    if guard:
        return guard
    from services import category_service
    from schemas import CategoryCreate
    from pydantic import ValidationError

    name = request.form.get("name", "").strip()
    parent_id = request.form.get("parent_id")
    if parent_id == "":
        parent_id = None
    elif parent_id is not None:
        parent_id = int(parent_id)

    try:
        data = CategoryCreate(name=name, parent_id=parent_id)
        category_service.create(data)
        flash("Category created.", "success")
    except ValidationError as exc:
        msg = "; ".join(f"{e['loc'][0]}: {e['msg']}" for e in exc.errors() if e.get("loc"))
        flash(msg or "Validation failed.", "error")
    except Exception as e:
        flash(getattr(e, "message", "Could not create category."), "error")

    return redirect(url_for("web_admin.admin_categories"))


@admin_web_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
def admin_category_delete(category_id: int):
    guard = require_admin()
    if guard:
        return guard
    from services import category_service
    try:
        category_service.delete(category_id)
        flash("Category deleted.", "success")
    except Exception as e:
        flash(getattr(e, "message", "Could not delete category."), "error")
    return redirect(url_for("web_admin.admin_categories"))
