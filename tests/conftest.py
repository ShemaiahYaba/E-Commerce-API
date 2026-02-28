"""Pytest fixtures: app, client, db, auth headers."""

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


def _register_and_login(client, email: str, password: str, first_name: str = "Test", last_name: str = "User"):
    """Register user and return (headers dict, user_id from response)."""
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    assert r.status_code == 201
    data = r.get_json()["data"]
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}, data.get("user", {}).get("id")


@pytest.fixture
def customer_headers(client):
    """Auth headers for a registered customer."""
    headers, _ = _register_and_login(client, "customer@test.com", "password123")
    return headers


@pytest.fixture
def admin_headers(client, db):
    """Auth headers for an admin user (created in DB)."""
    from models import User
    from utils.security import hash_password
    with client.application.app_context():
        admin = User(
            email="admin@test.com",
            password_hash=hash_password("admin123"),
            first_name="Admin",
            last_name="User",
            role="admin",
        )
        _db.session.add(admin)
        _db.session.commit()
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin123"},
    )
    assert r.status_code == 200
    token = r.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
