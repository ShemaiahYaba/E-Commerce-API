"""Health and root (info) routes."""

from flask import Blueprint
from http import HTTPStatus
from utils.responses import success_response

info_bp = Blueprint("info", __name__)


@info_bp.route("/", methods=["GET"])
def root() -> tuple:
    """Root: API name and version.
    ---
    tags: [info]
    responses:
      200:
        description: API name and version
    """
    return success_response(
        data={"name": "E-Commerce API", "version": "1.0"},
        status=HTTPStatus.OK,
    )


@info_bp.route("/health", methods=["GET"])
def health() -> tuple:
    """Health check.
    ---
    tags: [info]
    responses:
      200:
        description: Service health status
    """
    return success_response(data={"status": "ok"}, status=HTTPStatus.OK)
