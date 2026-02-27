"""Auth and user route tests."""

import pytest


def test_register_success(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@test.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
        },
    )
    assert r.status_code == 201
    data = r.get_json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == "new@test.com"


def test_register_duplicate_email(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@test.com",
            "password": "password123",
            "first_name": "A",
            "last_name": "B",
        },
    )
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@test.com",
            "password": "other123",
            "first_name": "C",
            "last_name": "D",
        },
    )
    assert r.status_code == 409


def test_login_success(client, db):
    from database import db as _db
    from models import User
    from utils.security import hash_password
    with client.application.app_context():
        u = User(
            email="login@test.com",
            password_hash=hash_password("secret123"),
            first_name="L",
            last_name="U",
        )
        _db.session.add(u)
        _db.session.commit()
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "secret123"},
    )
    assert r.status_code == 200
    assert "access_token" in r.get_json()["data"]


def test_login_wrong_password(client, db):
    from database import db as _db
    from models import User
    from utils.security import hash_password
    with client.application.app_context():
        u = User(
            email="wrong@test.com",
            password_hash=hash_password("secret123"),
            first_name="W",
            last_name="U",
        )
        _db.session.add(u)
        _db.session.commit()
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@test.com", "password": "wrong"},
    )
    assert r.status_code == 401


def test_me_requires_auth(client):
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401
