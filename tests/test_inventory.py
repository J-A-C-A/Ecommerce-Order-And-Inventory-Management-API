import pytest

@pytest.mark.asyncio
async def test_get_inventory(client, admin_auth_headers, created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 10,
    }
    post_response = await client.post("/products", json=payload, headers=admin_auth_headers)
    product_id = post_response.json()["product_id"]
    response = await client.get(f"/inventory/{product_id}", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_id
    assert data["quantity_total"] == 10
    assert data["quantity_reserved"] == 0

@pytest.mark.asyncio
async def test_get_inventory_not_found(client, admin_auth_headers):
    response = await client.get("/inventory/999", headers=admin_auth_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_inventory_forbidden_for_customer(client, admin_auth_headers, customer_auth_headers, created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 10,
    }
    post_response = await client.post("/products", json=payload, headers=admin_auth_headers)
    product_id = post_response.json()["product_id"]
    response = await client.get(f"/inventory/{product_id}", headers=customer_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_inventory_success(client, admin_auth_headers, created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 10,
    }
    post_response = await client.post("/products", json=payload, headers=admin_auth_headers)
    product_id = post_response.json()["product_id"]
    update_payload = {
        "quantity_total": 20
    }
    response = await client.patch(f"/inventory/{product_id}", json=update_payload, headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_id
    assert data["quantity_total"] == 20

@pytest.mark.asyncio
async def test_update_inventory_not_found(client, admin_auth_headers):
    response = await client.patch(
        "/inventory/999",
        json={"quantity_total": 20},
        headers=admin_auth_headers
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_inventory_forbidden_for_customer(client, admin_auth_headers, customer_auth_headers,
                                                       created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 10,
    }
    post_response = await client.post("/products", json=payload, headers=admin_auth_headers)
    product_id = post_response.json()["product_id"]
    update_payload = {
        "quantity_total": 20
    }
    response = await client.patch(f"/inventory/{product_id}", json=update_payload, headers=customer_auth_headers)
    assert response.status_code == 403