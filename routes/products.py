"""Product routes: list (search), get, create, update, delete, image upload (admin for write)."""

import os
from flask import Blueprint, request, current_app
from http import HTTPStatus
from pydantic import ValidationError
from werkzeug.utils import secure_filename

from schemas import ProductCreate, ProductUpdate, ProductResponse, ProductImageCreate
from services import product_service
from middleware.auth import admin_required
from flask_jwt_extended import jwt_required
from utils.responses import success_response, error_response

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@products_bp.route("", methods=["GET"])
def list_products():
    """List products with search and filters (public).
    ---
    tags: [products]
    parameters:
      - name: q
        in: query
        type: string
      - name: category_id
        in: query
        type: integer
      - name: page
        in: query
        type: integer
      - name: per_page
        in: query
        type: integer
    responses:
      200:
        description: Paginated products
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("q", "").strip() or None
    category_id = request.args.get("category_id", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_rating = request.args.get("min_rating", type=float)
    in_stock_only = request.args.get("in_stock_only", "false").lower() == "true"
    result = product_service.get_all_paginated(
        page=page,
        per_page=per_page,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        in_stock_only=in_stock_only,
    )
    products = result.pop("products")
    return success_response(
        data={
            "products": [ProductResponse.model_validate(p).model_dump() for p in products],
            **result,
        }
    )


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id: int):
    """Get product by id (public).
    ---
    tags: [products]
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Product
      404:
        description: Not found
    """
    try:
        p = product_service.get_by_id(product_id)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(data=ProductResponse.model_validate(p).model_dump())


@products_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_product():
    """Create product (admin).
    ---
    tags: [products]
    security: [Bearer: []]
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [name, price, sku, category_id]
          properties:
            name: { type: string }
            description: { type: string }
            price: { type: number }
            stock: { type: integer }
            sku: { type: string }
            category_id: { type: integer }
    responses:
      201:
        description: Product created
    """
    try:
        data = ProductCreate.model_validate(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    try:
        p = product_service.create(data)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(
        data=ProductResponse.model_validate(p).model_dump(),
        status=HTTPStatus.CREATED,
    )


@products_bp.route("/<int:product_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_product(product_id: int):
    """Update product (admin).
    ---
    tags: [products]
    security: [Bearer: []]
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name: { type: string }
            price: { type: number }
            stock: { type: integer }
            sku: { type: string }
    responses:
      200:
        description: Product updated
    """
    try:
        data = ProductUpdate.model_validate(request.get_json() or {})
    except ValidationError as e:
        return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
    try:
        p = product_service.update(product_id, data)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return success_response(data=ProductResponse.model_validate(p).model_dump())


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_product(product_id: int):
    """Delete product (admin).
    ---
    tags: [products]
    security: [Bearer: []]
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Product deleted
    """
    try:
        product_service.delete(product_id)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    return "", HTTPStatus.NO_CONTENT


@products_bp.route("/<int:product_id>/images", methods=["POST"])
@jwt_required()
@admin_required
def add_product_image(product_id: int):
    """Upload or add product image (admin).
    ---
    tags: [products]
    security: [Bearer: []]
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            url: { type: string }
            sort_order: { type: integer }
    responses:
      201:
        description: Image added
    """
    if request.is_json:
        try:
            data = ProductImageCreate.model_validate(request.get_json())
        except ValidationError as e:
            return error_response("Validation failed", HTTPStatus.BAD_REQUEST, e.errors())
        try:
            img = product_service.add_image(product_id, data.url, data.sort_order)
        except Exception as e:
            if hasattr(e, "status_code"):
                return error_response(e.message, e.status_code)
            raise
        from schemas import ProductImageResponse
        return success_response(
            data=ProductImageResponse.model_validate(img).model_dump(),
            status=HTTPStatus.CREATED,
        )
    file = request.files.get("file")
    if not file or file.filename == "":
        return error_response("No file or url provided", HTTPStatus.BAD_REQUEST)
    if not allowed_file(file.filename):
        return error_response("Invalid file type", HTTPStatus.BAD_REQUEST)
    filename = secure_filename(file.filename)
    upload_dir = current_app.config.get("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, f"product_{product_id}_{filename}")
    file.save(path)
    url = f"/uploads/product_{product_id}_{filename}"
    try:
        img = product_service.add_image(product_id, url, 0)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_response(e.message, e.status_code)
        raise
    from schemas import ProductImageResponse
    return success_response(
        data=ProductImageResponse.model_validate(img).model_dump(),
        status=HTTPStatus.CREATED,
    )
