import pytest

from app.models import CartItem
from sqlalchemy import select

@pytest.mark.asyncio
async def test_get_cart_empty(client, customer_auth_headers):
    response = await client.get("/cart", headers=customer_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["cart_items"] == []
    assert data["total_cart_price"] == "0"


@pytest.mark.asyncio
async def test_add_item_to_cart_success(client, created_product ,customer_auth_headers):
    product = created_product
    payload = {"product_id": product["product_id"],"product_quantity": 1}
    response = await client.post("/cart/items", json=payload, headers=customer_auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert len(data["cart_items"]) == 1
    assert data["total_cart_price"] == "10.00"
    assert data["cart_items"][0]["product"]["product_id"] == product["product_id"]
    assert data["cart_items"][0]["product_quantity"] == 1

@pytest.mark.asyncio
async def test_add_item_twice_increase_quantity(client, created_product ,customer_auth_headers):
    product = created_product
    payload = {"product_id": product["product_id"], "product_quantity": 1}
    post_response = await client.post("/cart/items", json=payload, headers=customer_auth_headers)
    post_response2 = await client.post("/cart/items", json=payload, headers=customer_auth_headers)

    assert post_response.status_code == 201
    assert post_response2.status_code == 201
    data = post_response2.json()
    assert len(data["cart_items"]) == 1
    assert data["total_cart_price"] == "20.00"
    assert data["cart_items"][0]["product"]["product_id"] == product["product_id"]
    assert data["cart_items"][0]["product_quantity"] == 2

@pytest.mark.asyncio
async def test_add_nonexistent_product_to_cart(client, customer_auth_headers):
    payload = {
        "product_id": 999,
        "product_quantity": 1
    }
    response = await client.post("/cart/items", json=payload, headers=customer_auth_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_cart_item_quantity(client, created_product ,customer_auth_headers):
    product = created_product
    product_id = product["product_id"]
    payload = {"product_id": product["product_id"], "product_quantity": 1}
    post_response = await client.post("/cart/items", json=payload, headers=customer_auth_headers)
    assert post_response.status_code == 201
    update_payload = {"product_quantity": 2}
    response = await client.patch(f"/cart/items/{product_id}", json=update_payload, headers=customer_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_cart_price"] == "20.00"
    assert data["cart_items"][0]["product"]["product_id"] == product["product_id"]
    assert data["cart_items"][0]["product_quantity"] == 2

@pytest.mark.asyncio
async def test_update_nonexistent_product_to_cart(client, created_product ,customer_auth_headers):
    update_payload = {"product_quantity": 2}
    response = await client.patch("/cart/items/99", json=update_payload, headers=customer_auth_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_remove_item_from_cart(client, created_product ,customer_auth_headers):
    product = created_product
    product_id = product["product_id"]
    payload = {"product_id": product_id, "product_quantity": 1}
    post_response = await client.post("/cart/items", json=payload, headers=customer_auth_headers)
    assert post_response.status_code == 201
    response = await client.delete(f"/cart/items/{product_id}", headers=customer_auth_headers)
    assert response.status_code == 204
    get_response = await client.get("/cart", headers=customer_auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["cart_items"] == []

@pytest.mark.asyncio
async def test_remove_all_items_from_cart(client, created_product, created_category ,customer_auth_headers,admin_auth_headers):
    product1 = created_product
    product1_id = product1["product_id"]

    product2_payload= {
        "product_name": "Test Product",
        "product_description": "Test Description",
        "is_active": True,
        "price": 20.00,
        "category_id": created_category["category_id"],
        "initial_quantity": 20,
    }

    product2_response = await client.post("/products", json=product2_payload, headers=admin_auth_headers)
    assert product2_response.status_code == 201
    product2_id = product2_response.json()["product_id"]
    product2_response2 = await client.post("/cart/items",json={"product_id": product2_id,"product_quantity": 1},headers=customer_auth_headers)
    assert product2_response2.status_code == 201

    product1_response1 = await client.post("/cart/items",json={"product_id": product1_id,"product_quantity": 1},headers=customer_auth_headers)
    assert product1_response1.status_code == 201

    response = await client.delete("/cart",headers=customer_auth_headers)
    assert response.status_code == 204
    get_response = await client.get("/cart", headers=customer_auth_headers)
    assert get_response.json()["cart_items"] == []

@pytest.mark.asyncio
async def test_cart_requires_authentication(client):
    response = await client.get("/cart")
    assert response.status_code == 401


