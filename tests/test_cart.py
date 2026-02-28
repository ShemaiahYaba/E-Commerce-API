"""Cart API tests: get, add, update, remove, clear."""

import pytest


@pytest.fixture
def category_and_product(client, admin_headers):
    """Create category and product; return (category_id, product_id)."""
    cat_r = client.post(
        "/api/v1/categories",
        json={"name": "CartCategory"},
        headers=admin_headers,
    )
    cat_id = cat_r.get_json()["data"]["id"]
    prod_r = client.post(
        "/api/v1/products",
        json={
            "name": "CartProduct",
            "price": 19.99,
            "stock": 10,
            "sku": "CART-001",
            "category_id": cat_id,
        },
        headers=admin_headers,
    )
    return cat_id, prod_r.get_json()["data"]["id"]


def test_get_cart_empty(client, customer_headers):
    r = client.get("/api/v1/cart", headers=customer_headers)
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["items"] == []
    assert data["total"] == "0" or data["total"] == "0.00"


def test_add_to_cart_and_get(client, customer_headers, category_and_product):
    _, product_id = category_and_product
    r = client.post(
        "/api/v1/cart/items",
        json={"product_id": product_id, "quantity": 2},
        headers=customer_headers,
    )
    assert r.status_code == 201
    data = r.get_json()["data"]
    assert data["product_id"] == product_id
    assert data["quantity"] == 2

    r2 = client.get("/api/v1/cart", headers=customer_headers)
    assert r2.status_code == 200
    items = r2.get_json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["quantity"] == 2


def test_add_to_cart_insufficient_stock(client, customer_headers, category_and_product):
    _, product_id = category_and_product
    r = client.post(
        "/api/v1/cart/items",
        json={"product_id": product_id, "quantity": 999},
        headers=customer_headers,
    )
    assert r.status_code == 400


def test_update_cart_item(client, customer_headers, category_and_product):
    _, product_id = category_and_product
    add_r = client.post(
        "/api/v1/cart/items",
        json={"product_id": product_id, "quantity": 3},
        headers=customer_headers,
    )
    item_id = add_r.get_json()["data"]["id"]

    r = client.put(
        f"/api/v1/cart/items/{item_id}",
        json={"quantity": 1},
        headers=customer_headers,
    )
    assert r.status_code == 200
    assert r.get_json()["data"]["quantity"] == 1


def test_remove_cart_item(client, customer_headers, category_and_product):
    _, product_id = category_and_product
    add_r = client.post(
        "/api/v1/cart/items",
        json={"product_id": product_id, "quantity": 1},
        headers=customer_headers,
    )
    item_id = add_r.get_json()["data"]["id"]

    r = client.delete(f"/api/v1/cart/items/{item_id}", headers=customer_headers)
    assert r.status_code == 204

    get_r = client.get("/api/v1/cart", headers=customer_headers)
    assert len(get_r.get_json()["data"]["items"]) == 0


def test_clear_cart(client, customer_headers, category_and_product):
    _, product_id = category_and_product
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product_id, "quantity": 1},
        headers=customer_headers,
    )
    r = client.delete("/api/v1/cart", headers=customer_headers)
    assert r.status_code == 200
    get_r = client.get("/api/v1/cart", headers=customer_headers)
    assert get_r.get_json()["data"]["items"] == []
