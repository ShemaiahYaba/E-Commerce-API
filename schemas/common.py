"""Common Pydantic schemas (pagination, message)."""

from pydantic import BaseModel, Field


class PaginationOut(BaseModel):
    """Pagination metadata in list responses."""

    page: int
    per_page: int
    total: int
    pages: int


class MessageOut(BaseModel):
    """Simple message response."""

    message: str
