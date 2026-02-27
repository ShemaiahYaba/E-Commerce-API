"""Pydantic schemas for request/response."""

from .common import PaginationOut, MessageOut
from .auth import LoginRequest, TokenResponse
from .user import UserCreate, UserUpdate, UserResponse
from .category import CategoryCreate, CategoryUpdate, CategoryResponse
from .product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductImageCreate,
    ProductImageResponse,
)
from .cart import CartItemAdd, CartItemUpdate, CartItemResponse, CartResponse
from .order import OrderResponse, OrderItemResponse, OrderStatusUpdate
from .review import ReviewCreate, ReviewResponse
from .wishlist import WishlistAdd, WishlistItemResponse

__all__ = [
    "LoginRequest",
    "TokenResponse",
    "PaginationOut",
    "MessageOut",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductImageCreate",
    "ProductImageResponse",
    "CartItemAdd",
    "CartItemUpdate",
    "CartItemResponse",
    "CartResponse",
    "OrderResponse",
    "OrderItemResponse",
    "OrderStatusUpdate",
    "ReviewCreate",
    "ReviewResponse",
    "WishlistAdd",
    "WishlistItemResponse",
]
