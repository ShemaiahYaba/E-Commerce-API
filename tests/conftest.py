"""Pytest fixtures: app, client, db."""

import pytest
from app import create_app
from database import db as _db


@pytest.fixture
def app():
    """Create app for testing (in-memory SQLite)."""
    app = create_app("testing")
    return app


@pytest.fixture
def db(app):
    """Database with tables created and torn down."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Test client; db fixture ensures tables exist."""
    return app.test_client()
