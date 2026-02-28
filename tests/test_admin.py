"""Admin API tests: stats, inventory, list orders."""

import pytest


def test_admin_stats_requires_auth(client):
    r = client.get("/api/v1/admin/stats")
    assert r.status_code == 401


def test_admin_stats_requires_admin(client, customer_headers):
    r = client.get("/api/v1/admin/stats", headers=customer_headers)
    assert r.status_code == 403


def test_admin_stats_success(client, admin_headers):
    r = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert "total_users" in data
    assert "total_orders" in data
    assert "revenue" in data
    assert "popular_products" in data


def test_admin_inventory(client, admin_headers):
    r = client.get("/api/v1/admin/inventory", headers=admin_headers)
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert "products" in data
    assert "low_stock" in data


def test_admin_orders_list(client, admin_headers):
    r = client.get("/api/v1/admin/orders", headers=admin_headers)
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert "orders" in data
