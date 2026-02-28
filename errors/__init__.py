# errors package — re-exports for backwards compatibility
from errors.exceptions import (
    AppException,
    DuplicateEmailError,
    InvalidCredentialsError,
    UserNotFoundError,
    CategoryNotFoundError,
    ProductNotFoundError,
    DuplicateSKUError,
    OrderNotFoundError,
    ValidationError,
    DatabaseError,
    RateLimitError,
)
from errors.handlers import register_error_handlers

__all__ = [
    "AppException",
    "DuplicateEmailError",
    "InvalidCredentialsError",
    "UserNotFoundError",
    "CategoryNotFoundError",
    "ProductNotFoundError",
    "DuplicateSKUError",
    "OrderNotFoundError",
    "ValidationError",
    "DatabaseError",
    "RateLimitError",
    "register_error_handlers",
]
