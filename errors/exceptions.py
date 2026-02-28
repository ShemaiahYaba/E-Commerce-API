"""Custom exceptions with message and status_code for error handlers."""


class AppException(Exception):
    """Base app exception; map to JSON error response."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DuplicateEmailError(AppException):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email {email} already exists", 409)


class InvalidCredentialsError(AppException):
    def __init__(self, message: str = "Invalid email or password") -> None:
        super().__init__(message, 401)


class UserNotFoundError(AppException):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"User with ID {user_id} not found", 404)


class CategoryNotFoundError(AppException):
    def __init__(self, category_id: int) -> None:
        super().__init__(f"Category with ID {category_id} not found", 404)


class ProductNotFoundError(AppException):
    def __init__(self, product_id: int) -> None:
        super().__init__(f"Product with ID {product_id} not found", 404)


class DuplicateSKUError(AppException):
    def __init__(self, sku: str) -> None:
        super().__init__(f"SKU {sku} already exists", 409)


class OrderNotFoundError(AppException):
    def __init__(self, order_id: int) -> None:
        super().__init__(f"Order with ID {order_id} not found", 404)


class ValidationError(AppException):
    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message, 400)
        self.field = field


class DatabaseError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, 500)


class RateLimitError(AppException):
    def __init__(self, message: str = "Too many requests. Please slow down.") -> None:
        super().__init__(message, 429)
