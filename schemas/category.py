"""Category request/response schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    """Create category."""

    name: str = Field(..., min_length=1, max_length=100)
    parent_id: int | None = None


class CategoryUpdate(BaseModel):
    """Update category."""

    name: str | None = Field(None, min_length=1, max_length=100)
    parent_id: int | None = None


class CategoryResponse(BaseModel):
    """Category in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None
    created_at: datetime
