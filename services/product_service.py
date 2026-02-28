"""Product service: CRUD, full search, pagination, image upload."""

from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func

from database import db
from models import Product, ProductImage, Category, Review
from schemas import ProductCreate, ProductUpdate
from exceptions import ProductNotFoundError, CategoryNotFoundError, DuplicateSKUError
from services.base_service import BaseService


def _build_query(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    in_stock_only: bool = False,
):
    """Build product query with filters (private helper)."""
    q = Product.query.filter(Product.is_active == True)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%") | Product.description.ilike(f"%{search}%"))
    if category_id is not None:
        q = q.filter(Product.category_id == category_id)
    if min_price is not None:
        q = q.filter(Product.price >= Decimal(str(min_price)))
    if max_price is not None:
        q = q.filter(Product.price <= Decimal(str(max_price)))
    if in_stock_only:
        q = q.filter(Product.stock > 0)
    if min_rating is not None:
        subq = (
            db.session.query(Review.product_id, func.avg(Review.rating).label("avg_rating"))
            .group_by(Review.product_id)
            .having(func.avg(Review.rating) >= min_rating)
            .subquery()
        )
        q = q.join(subq, Product.id == subq.c.product_id)
    return q


def _verify_category_exists(category_id: int) -> None:
    """Raise CategoryNotFoundError if category does not exist."""
    if db.session.get(Category, category_id) is None:
        raise CategoryNotFoundError(category_id)


def _check_duplicate_sku(sku: str, exclude_product_id: Optional[int] = None) -> None:
    """Raise DuplicateSKUError if sku already exists (optionally excluding one product)."""
    query = Product.query.filter_by(sku=sku.strip())
    if exclude_product_id is not None:
        query = query.filter(Product.id != exclude_product_id)
    if query.first():
        raise DuplicateSKUError(sku)


def _create_product_object(data: ProductCreate) -> Product:
    """Build Product instance from schema (private helper)."""
    return Product(
        name=data.name.strip(),
        description=data.description.strip() if data.description else None,
        price=data.price,
        stock=data.stock,
        sku=data.sku.strip(),
        category_id=data.category_id,
        is_active=data.is_active,
    )


def get_all_paginated(
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    in_stock_only: bool = False,
) -> dict:
    """List products with filters and pagination."""
    per_page = min(per_page, 100)
    q = _build_query(search, category_id, min_price, max_price, min_rating, in_stock_only)
    total = q.count()
    items = q.order_by(Product.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    pagination = BaseService.pagination_dict(total, page, per_page)
    return {"products": items, **pagination}


def get_by_id(product_id: int) -> Product:
    """Get product by id; raise ProductNotFoundError if missing."""
    p = db.session.get(Product, product_id)
    if not p:
        raise ProductNotFoundError(product_id)
    return p


def create(data: ProductCreate) -> Product:
    """Create product (admin)."""
    _verify_category_exists(data.category_id)
    _check_duplicate_sku(data.sku)
    product = _create_product_object(data)
    db.session.add(product)
    db.session.commit()
    db.session.refresh(product)
    return product


def update(product_id: int, data: ProductUpdate) -> Product:
    """Update product (admin)."""
    p = get_by_id(product_id)
    payload = data.model_dump(exclude_unset=True)
    if "sku" in payload and payload["sku"] != p.sku:
        _check_duplicate_sku(payload["sku"], exclude_product_id=product_id)
    if "category_id" in payload:
        _verify_category_exists(payload["category_id"])
    for k, v in payload.items():
        if k == "description":
            setattr(p, k, v.strip() if v else None)
        elif k == "name" or k == "sku":
            setattr(p, k, v.strip() if v else v)
        else:
            setattr(p, k, v)
    db.session.commit()
    db.session.refresh(p)
    return p


def delete(product_id: int) -> None:
    """Delete product (admin)."""
    p = get_by_id(product_id)
    db.session.delete(p)
    db.session.commit()


def add_image(product_id: int, url: str, sort_order: int = 0) -> ProductImage:
    """Add image to product."""
    p = get_by_id(product_id)
    img = ProductImage(product_id=p.id, url=url, sort_order=sort_order)
    db.session.add(img)
    db.session.commit()
    db.session.refresh(img)
    return img
