"""Register global error handlers on the Flask app."""

from flask import Flask
from pydantic import ValidationError as PydanticValidationError

from exceptions import AppException
from utils.responses import error_response
from http import HTTPStatus


def register_error_handlers(app: Flask) -> None:
    """Attach handlers for AppException, Pydantic, 404, 500."""

    @app.errorhandler(AppException)
    def handle_app_exception(e: AppException):
        return error_response(e.message, e.status_code)

    @app.errorhandler(PydanticValidationError)
    def handle_pydantic_validation(e: PydanticValidationError):
        errors = [{"loc": err.get("loc"), "msg": err.get("msg")} for err in e.errors()]
        return error_response("Validation failed", HTTPStatus.UNPROCESSABLE_ENTITY, errors=errors)

    @app.errorhandler(404)
    def handle_not_found(e):
        return error_response("Resource not found", 404)

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return error_response("Method not allowed", 405)

    @app.errorhandler(500)
    def handle_internal(e):
        app.logger.exception("Internal server error")
        return error_response("Internal server error", 500)
