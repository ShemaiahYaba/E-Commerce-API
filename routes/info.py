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
    db_ok = True
    try:
        from database import db
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
    except Exception:
        db_ok = False

    from datetime import datetime
    return success_response(data={
        "status": "ok",
        "db_ok": db_ok,
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat()
    }, status=HTTPStatus.OK)
