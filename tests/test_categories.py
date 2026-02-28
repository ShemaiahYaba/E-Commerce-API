"""Category API tests: list, get, create, update, delete (admin)."""

import pytest


def test_list_categories_empty(client):
    r = client.get("/api/v1/categories")
    assert r.status_code == 200
    data = r.get_json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_category_not_found(client):
    r = client.get("/api/v1/categories/99999")
    assert r.status_code == 404


def test_create_category_requires_auth(client):
    r = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
    )
    assert r.status_code == 401


def test_create_category_requires_admin(client, customer_headers):
    r = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=customer_headers,
    )
    assert r.status_code == 403


def test_create_and_list_category(client, admin_headers):
    r = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers=admin_headers,
    )
    assert r.status_code == 201
    data = r.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Electronics"
    assert "id" in data["data"]

    r2 = client.get("/api/v1/categories")
    assert r2.status_code == 200
    items = r2.get_json()["data"]
    assert len(items) >= 1
    names = [c["name"] for c in items]
    assert "Electronics" in names


def test_get_category_by_id(client, admin_headers):
    create_r = client.post(
        "/api/v1/categories",
        json={"name": "Books"},
        headers=admin_headers,
    )
    assert create_r.status_code == 201
    cat_id = create_r.get_json()["data"]["id"]

    r = client.get(f"/api/v1/categories/{cat_id}")
    assert r.status_code == 200
    assert r.get_json()["data"]["name"] == "Books"


def test_update_category(client, admin_headers):
    create_r = client.post(
        "/api/v1/categories",
        json={"name": "Toys"},
        headers=admin_headers,
    )
    cat_id = create_r.get_json()["data"]["id"]

    r = client.put(
        f"/api/v1/categories/{cat_id}",
        json={"name": "Toys & Games"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.get_json()["data"]["name"] == "Toys & Games"


def test_delete_category(client, admin_headers):
    create_r = client.post(
        "/api/v1/categories",
        json={"name": "DeleteMe"},
        headers=admin_headers,
    )
    cat_id = create_r.get_json()["data"]["id"]

    r = client.delete(f"/api/v1/categories/{cat_id}", headers=admin_headers)
    assert r.status_code == 204

    get_r = client.get(f"/api/v1/categories/{cat_id}")
    assert get_r.status_code == 404
