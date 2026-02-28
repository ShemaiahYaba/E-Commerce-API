"""Product API tests: list, get, create, update, delete, search (admin for write)."""

import pytest


@pytest.fixture
def category_id(client, admin_headers):
    """Create a category and return its id."""
    r = client.post(
        "/api/v1/categories",
        json={"name": "TestCategory"},
        headers=admin_headers,
    )
    assert r.status_code == 201
    return r.get_json()["data"]["id"]


def test_list_products_empty(client):
    r = client.get("/api/v1/products")
    assert r.status_code == 200
    data = r.get_json()
    assert data["success"] is True
    assert "data" in data
    assert "products" in data["data"]
    assert "total" in data["data"]


def test_create_product_requires_admin(client, customer_headers, category_id):
    r = client.post(
        "/api/v1/products",
        json={
            "name": "Widget",
            "price": 9.99,
            "stock": 10,
            "sku": "WID-001",
            "category_id": category_id,
        },
        headers=customer_headers,
    )
    assert r.status_code == 403


def test_create_and_get_product(client, admin_headers, category_id):
    r = client.post(
        "/api/v1/products",
        json={
            "name": "Widget",
            "description": "A nice widget",
            "price": 9.99,
            "stock": 10,
            "sku": "WID-001",
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    assert r.status_code == 201
    data = r.get_json()["data"]
    assert data["name"] == "Widget"
    assert data["sku"] == "WID-001"
    product_id = data["id"]

    r2 = client.get(f"/api/v1/products/{product_id}")
    assert r2.status_code == 200
    assert r2.get_json()["data"]["name"] == "Widget"


def test_create_product_duplicate_sku(client, admin_headers, category_id):
    payload = {
        "name": "Widget A",
        "price": 1.0,
        "stock": 1,
        "sku": "DUP-SKU",
        "category_id": category_id,
    }
    client.post("/api/v1/products", json=payload, headers=admin_headers)
    r = client.post("/api/v1/products", json={**payload, "name": "Widget B"}, headers=admin_headers)
    assert r.status_code == 409


def test_list_products_search(client, admin_headers, category_id):
    client.post(
        "/api/v1/products",
        json={
            "name": "Blue Widget",
            "price": 5.0,
            "stock": 5,
            "sku": "BLUE-1",
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    r = client.get("/api/v1/products?q=Blue")
    assert r.status_code == 200
    products = r.get_json()["data"]["products"]
    assert any(p["name"] == "Blue Widget" for p in products)


def test_delete_product(client, admin_headers, category_id):
    create_r = client.post(
        "/api/v1/products",
        json={
            "name": "DeleteMe",
            "price": 1.0,
            "stock": 1,
            "sku": "DEL-1",
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    pid = create_r.get_json()["data"]["id"]
    r = client.delete(f"/api/v1/products/{pid}", headers=admin_headers)
    assert r.status_code == 204
    get_r = client.get(f"/api/v1/products/{pid}")
    assert get_r.status_code == 404
