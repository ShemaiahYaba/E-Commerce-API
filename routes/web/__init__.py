"""Web UI package — docs landing page + sub-blueprint registration."""

from flask import Blueprint, render_template
from routes.web.auth import auth_web_bp
from routes.web.products import products_web_bp
from routes.web.cart import cart_web_bp
from routes.web.orders import orders_web_bp
from routes.web.admin import admin_web_bp

# Docs-landing blueprint (keeps /web/docs)
docs_web_bp = Blueprint(
    "web_docs", __name__, url_prefix="/web", template_folder="../../templates"
)


@docs_web_bp.route("/docs")
def index():
    """Webdocs landing: links to Swagger and endpoint list."""
    return render_template("webdocs/index.html")


def register_web_blueprints(app):
    """Register all web UI blueprints onto the app."""
    for bp in (auth_web_bp, products_web_bp, cart_web_bp, orders_web_bp, admin_web_bp, docs_web_bp):
        app.register_blueprint(bp)
