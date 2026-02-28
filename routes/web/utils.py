"""Shared utilities for web blueprint routes."""

from flask import redirect, url_for, session, flash


def require_login():
    """Return a redirect to login if user is unauthenticated, else None."""
    if not session.get("access_token"):
        flash("Please log in to continue.", "error")
        return redirect(url_for("web_auth.login"))
    return None
