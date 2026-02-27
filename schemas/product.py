"""Product and ProductImage schemas."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class ProductImageCreate(BaseModel):
    """Add image (url or path)."""

    url: str = Field(..., max_length=500)
    sort_order: int = 0


class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    url: str
    sort_order: int


class ProductCreate(BaseModel):
    """Create product (admin)."""

    name: str = Field(..., min_length=1, max_length=300)
    description: str | None = None
    price: Decimal = Field(..., ge=0)
    stock: int = Field(0, ge=0)
    sku: str = Field(..., min_length=1, max_length=50)
    category_id: int
    is_active: bool = True


class ProductUpdate(BaseModel):
    """Partial product update."""

    name: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = None
    price: Decimal | None = Field(None, ge=0)
    stock: int | None = Field(None, ge=0)
    sku: str | None = Field(None, min_length=1, max_length=50)
    category_id: int | None = None
    is_active: bool | None = None


class CategoryRef(BaseModel):
    id: int
    name: str


class ProductResponse(BaseModel):
    """Product in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    sku: str
    category_id: int
    is_active: bool
    created_at: datetime
