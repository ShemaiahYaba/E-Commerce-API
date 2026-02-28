"""Web UI product routes: list, detail."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services import product_service, category_service
from errors.exceptions import ProductNotFoundError
from routes.web.utils import require_login

products_web_bp = Blueprint(
    "web_products", __name__, url_prefix="/web", template_folder="../../templates"
)


@products_web_bp.route("/products")
def products_list():
    guard = require_login()
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


@products_web_bp.route("/products/<int:product_id>")
def product_detail(product_id: int):
    guard = require_login()
    if guard:
        return guard

    try:
        product = product_service.get_by_id(product_id)
    except ProductNotFoundError:
        flash("Product not found.", "error")
        return redirect(url_for("web_products.products_list"))
    except Exception:
        flash("Error loading product.", "error")
        return redirect(url_for("web_products.products_list"))

    return render_template("products/detail.html", product=product)
