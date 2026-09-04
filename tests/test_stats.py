import pytest
from datetime import date, timedelta

@pytest.mark.asyncio
async def test_order_count_by_status(client, shipped_order, delivered_order, admin_auth_headers, customer_auth_headers, created_cart_with_item):
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country",}
    post_response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert post_response.status_code == 201

    response = await client.get("/stats/count", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    counts = {item["status"]: item["count"] for item in data}
    assert counts["Pending"] == 1
    assert counts["Shipped"] == 1
    assert counts["Delivered"] == 1

@pytest.mark.asyncio
async def test_order_count_by_status_forbidden_for_customer(client, shipped_order, delivered_order,customer_auth_headers, created_cart_with_item):
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country",}
    post_response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert post_response.status_code == 201

    response = await client.get("/stats/count", headers=customer_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_revenue_by_period(client, admin_auth_headers, delivered_order):
    today_date = date.today()
    previous_date = today_date - timedelta(days=14)
    payload = {
        "start_date": previous_date,
        "end_date": today_date,
    }
    response = await client.get("/stats/revenue", params=payload, headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_revenue"] == "20.00"

@pytest.mark.asyncio
async def test_revenue_by_period_returns_zero_when_no_orders_in_period(client, admin_auth_headers):
    today_date = date.today()
    previous_date = today_date - timedelta(days=14)
    payload = {
        "start_date": previous_date,
        "end_date": today_date,
    }
    response = await client.get("/stats/revenue", params=payload, headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_revenue"] == "0.00"

@pytest.mark.asyncio
async def test_revenue_by_period_excludes_pending(client, admin_auth_headers, customer_auth_headers, created_cart_with_item):
    today_date = date.today()
    previous_date = today_date - timedelta(days=14)

    payload1 = {
        "street": "Przykładowa",
        "building_number": "1",
        "apartment_number": "1",
        "postal_code": "01-001",
        "city": "Default city",
        "country": "Default country",}

    payload2 = {
        "start_date": previous_date,
        "end_date": today_date,}

    order_response = await client.post("/orders",json=payload1,headers=customer_auth_headers)
    assert order_response.status_code == 201

    response = await client.get("/stats/revenue", params=payload2, headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_revenue"] == "0.00"

@pytest.mark.asyncio
async def test_revenue_by_period_forbidden_for_customer(client,  customer_auth_headers, delivered_order):
    today_date = date.today()
    previous_date = today_date - timedelta(days=14)
    payload = {
        "start_date": previous_date,
        "end_date": today_date,
    }
    response = await client.get("/stats/revenue", params=payload, headers=customer_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_top_selling_products(client, admin_auth_headers, delivered_order):
    product_id = delivered_order["product"]["product_id"]
    response = await client.get("/stats/top_products", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["product"]["product_id"] == product_id
    assert data[0]["total_sold"] == 2

@pytest.mark.asyncio
async def test_top_selling_products_returns_empty_list(client, admin_auth_headers):
    response = await client.get("/stats/top_products", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data == []

@pytest.mark.asyncio
async def test_top_selling_products_forbidden_for_customer(client, customer_auth_headers, delivered_order):
    response = await client.get("/stats/top_products", headers=customer_auth_headers)
    assert response.status_code == 403
