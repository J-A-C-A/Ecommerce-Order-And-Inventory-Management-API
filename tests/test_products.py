import pytest

@pytest.mark.asyncio
async def test_create_product_success(client, admin_auth_headers, created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product',
        'product_description': 'Test Description',
        'is_active': True,
        'price': 20.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }
    response = await client.post("/products", json=payload, headers=admin_auth_headers)
    data = response.json()
    assert response.status_code == 201
    assert data['product_name'] == payload['product_name']
    assert data["category"] == category
    assert data["product_description"] == payload["product_description"]
    assert data["is_active"] == payload["is_active"]
    assert data["price"] == "20.00"

@pytest.mark.asyncio
async def test_create_product_forbidden_for_customer(client, customer_auth_headers, created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product',
        'product_description': 'Test Description',
        'is_active': True,
        'price': 20.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }
    response = await client.post("/products", json=payload, headers=customer_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_product_by_id_success(client,admin_auth_headers,created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product',
        'product_description': 'Test Description',
        'is_active': True,
        'price': 20.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }
    post_response = await client.post("/products", json=payload, headers=admin_auth_headers)
    product_id = post_response.json()["product_id"]
    response = await client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["product_name"] == payload["product_name"]
    assert response.json()["product_id"] == product_id

@pytest.mark.asyncio
async def test_get_product_by_id_not_found(client):
    response = await client.get("/products/1234")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

@pytest.mark.asyncio
async def test_search_products_no_filters(client,admin_auth_headers,created_category):
    category = created_category
    payload1 = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }

    payload2 = {
        'product_name': 'Test Product 2',
        'product_description': 'Test Description 2',
        'is_active': True,
        'price': 20.00,
        'category_id': category["category_id"],
        'initial_quantity': 2,
    }
    await client.post("/products", json=payload1, headers=admin_auth_headers)
    await client.post("/products", json=payload2, headers=admin_auth_headers)
    response = await client.get("/products")
    data = response.json()
    assert response.status_code == 200
    assert len(data["products"]) == 2
    names = [product["product_name"] for product in data["products"]]
    assert set(names) == {"Test Product 1", "Test Product 2"}
    assert data["total"] == 2
    assert data["number_of_pages"] == 1
    assert data["page_size"] == 20

@pytest.mark.asyncio
async def test_search_products_by_category(client,admin_auth_headers,created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }
    await client.post("/products", json=payload, headers=admin_auth_headers)
    response = await client.get("/products", params={'category_id': category["category_id"]})
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["number_of_pages"] == 1
    assert response.json()["products"][0]["category"]["category_id"] == category["category_id"]

@pytest.mark.asyncio
async def test_search_products_by_price_range(client,admin_auth_headers,created_category):
    category = created_category
    payload1 = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }

    payload2 = {
        'product_name': 'Test Product 2',
        'product_description': 'Test Description 2',
        'is_active': True,
        'price': 15.00,
        'category_id': category["category_id"],
        'initial_quantity': 2,
    }
    await client.post("/products", json=payload1, headers=admin_auth_headers)
    await client.post("/products", json=payload2, headers=admin_auth_headers)
    response = await client.get("/products", params= {"min_price": 5.00, "max_price": 20.0})
    data = response.json()
    assert response.status_code == 200
    assert len(data["products"]) == 2
    names = [product["product_name"] for product in data["products"]]
    assert set(names) == {"Test Product 1", "Test Product 2"}
    assert data["total"] == 2
    assert data["number_of_pages"] == 1

@pytest.mark.asyncio
async def test_search_products_pagination(client,admin_auth_headers,created_category):
    category = created_category
    payload1 = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }
    category = created_category
    payload2 = {
        'product_name': 'Test Product 2',
        'product_description': 'Test Description 2',
        'is_active': True,
        'price': 15.00,
        'category_id': category["category_id"],
        'initial_quantity': 2,
    }
    await client.post("/products", json=payload1, headers=admin_auth_headers)
    await client.post("/products", json=payload2, headers=admin_auth_headers)
    response = await client.get("/products", params={"page": 2, "page_size": 1})
    data = response.json()
    assert len(data["products"]) == 1
    assert data["products"][0]["product_name"] == "Test Product 2"
    assert data["page_size"] == 1
    assert data["total"] == 2
    assert data["number_of_pages"] == 2

@pytest.mark.asyncio
async def test_update_product_success(client,admin_auth_headers,created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }
    post_response = await client.post("/products", json=payload, headers=admin_auth_headers)
    product_id = post_response.json()["product_id"]
    response = await client.patch(f"/products/{product_id}", json={"product_name": "New test name"}, headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["product_name"] == "New test name"

@pytest.mark.asyncio
async def test_update_product_not_found(client,admin_auth_headers,created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }
    post_response = await client.post("/products", json=payload, headers=admin_auth_headers)
    response = await client.patch("/products/99", json={"product_name": "New test name"},headers=admin_auth_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_product(client,admin_auth_headers,created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }
    post_response = await client.post("/products", json=payload, headers=admin_auth_headers)
    product_id = post_response.json()["product_id"]
    response1 = await client.delete(f"/products/{product_id}", headers=admin_auth_headers)
    assert response1.status_code == 204
    response2 = await client.get(f"/products/{product_id}")
    data = response2.json()
    assert data["is_active"] is False

@pytest.mark.asyncio
async def test_delete_product_not_found(client,admin_auth_headers,created_category):
    category = created_category
    payload = {
        'product_name': 'Test Product 1',
        'product_description': 'Test Description 1',
        'is_active': True,
        'price': 10.00,
        'category_id': category["category_id"],
        'initial_quantity': 1,
    }
    post_response = await client.post("/products", json=payload, headers=admin_auth_headers)
    response = await client.delete("/products/99", headers=admin_auth_headers)
    assert response.status_code == 404

