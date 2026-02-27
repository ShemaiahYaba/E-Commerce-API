"""Webdocs UI: minimal Jinja + Tailwind pages (Phase 7)."""

from flask import Blueprint, render_template

webdocs_bp = Blueprint("webdocs", __name__, url_prefix="/web", template_folder="../templates")


@webdocs_bp.route("/docs")
def index():
    """Webdocs landing: links to Swagger and endpoint list."""
    return render_template("webdocs/index.html")
