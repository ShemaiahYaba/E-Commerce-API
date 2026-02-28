"""Wishlist API tests: get, add, remove."""

import pytest


@pytest.fixture
def product_id(client, admin_headers):
    cat_r = client.post(
        "/api/v1/categories",
        json={"name": "WishCat"},
        headers=admin_headers,
    )
    cat_id = cat_r.get_json()["data"]["id"]
    prod_r = client.post(
        "/api/v1/products",
        json={
            "name": "WishProduct",
            "price": 99.0,
            "stock": 1,
            "sku": "WISH-001",
            "category_id": cat_id,
        },
        headers=admin_headers,
    )
    return prod_r.get_json()["data"]["id"]


def test_get_wishlist_empty(client, customer_headers):
    r = client.get("/api/v1/wishlist", headers=customer_headers)
    assert r.status_code == 200
    assert r.get_json()["data"] == []


def test_add_and_get_wishlist(client, customer_headers, product_id):
    r = client.post(
        "/api/v1/wishlist",
        json={"product_id": product_id},
        headers=customer_headers,
    )
    assert r.status_code == 201
    assert r.get_json()["data"]["product_id"] == product_id

    r2 = client.get("/api/v1/wishlist", headers=customer_headers)
    assert r2.status_code == 200
    items = r2.get_json()["data"]
    assert len(items) == 1
    assert items[0]["product_id"] == product_id


def test_remove_from_wishlist(client, customer_headers, product_id):
    client.post(
        "/api/v1/wishlist",
        json={"product_id": product_id},
        headers=customer_headers,
    )
    r = client.delete(f"/api/v1/wishlist/{product_id}", headers=customer_headers)
    assert r.status_code == 204
    r2 = client.get("/api/v1/wishlist", headers=customer_headers)
    assert r2.get_json()["data"] == []
