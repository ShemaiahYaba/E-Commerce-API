"""Standard JSON response helpers."""

from typing import Any
from flask import jsonify
from http import HTTPStatus


def success_response(
    data: Any = None,
    message: str = "",
    status: int = HTTPStatus.OK,
) -> tuple:
    """Return (json_body, status_code) for success."""
    body = {"success": True, "status": status}
    if message:
        body["message"] = message
    if data is not None:
        body["data"] = data
    return jsonify(body), status


def error_response(
    message: str,
    status: int = HTTPStatus.BAD_REQUEST,
    errors: list | None = None,
) -> tuple:
    """Return (json_body, status_code) for error."""
    body = {"success": False, "message": message, "status": status}
    if errors is not None:
        body["errors"] = errors
    return jsonify(body), status
