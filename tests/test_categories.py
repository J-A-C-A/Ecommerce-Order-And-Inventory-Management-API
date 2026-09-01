import pytest

@pytest.mark.asyncio
async def test_create_category_success(client, admin_auth_headers):
    payload = {
        "category_name": "test",
    }
    response = await client.post("/categories", json=payload, headers=admin_auth_headers)
    assert response.status_code == 201
    assert response.json()["category_name"] == "test"

@pytest.mark.asyncio
async def test_create_duplicate_fail(client, admin_auth_headers):
    payload1 = {
        "category_name": "test",
    }
    await client.post("/categories", json=payload1, headers=admin_auth_headers)
    payload2 = {
        "category_name": "test",
    }
    response = await client.post("/categories", json=payload2, headers=admin_auth_headers)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_category_forbidden(client,customer_auth_headers):
    payload1 = {
        "category_name": "test",
    }
    response = await client.post("/categories", json=payload1, headers=customer_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_category_by_id_success(client, admin_auth_headers):
    payload = {
        "category_name": "test",
    }
    post_response = await client.post("/categories", json=payload, headers=admin_auth_headers)
    category_id = post_response.json()["category_id"]
    response = await client.get(f"/categories/{category_id}")
    assert response.status_code == 200
    assert response.json()["category_name"] == "test"

@pytest.mark.asyncio
async def test_get_category_by_id_not_found(client):
    response = await client.get("/categories/9999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_all_categories_success(client,admin_auth_headers):
    payload1 = {
        "category_name": "test1",
    }
    payload2 = {
        "category_name": "test2",
    }
    await client.post("/categories", json=payload1, headers=admin_auth_headers)
    await client.post("/categories", json=payload2, headers=admin_auth_headers)
    response = await client.get("/categories", headers=admin_auth_headers)
    data = response.json()
    assert len(data) == 2
    names = [category["category_name"] for category in data]
    assert set(names) == {"test1", "test2"}
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_category_success(client,admin_auth_headers):
    payload1 = {
        "category_name": "test1",
    }
    payload2 = {
        "category_name": "test2",
    }
    post_response = await client.post("/categories", json=payload1, headers=admin_auth_headers)
    category_id = post_response.json()["category_id"]
    response = await client.patch(f"/categories/{category_id}", json=payload2, headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["category_name"] == "test2"

@pytest.mark.asyncio
async def test_update_category_not_found(client,admin_auth_headers):
    payload1 = {
        "category_name": "test1",
    }
    payload2 = {
        "category_name": "test2",
    }
    await client.post("/categories", json=payload1, headers=admin_auth_headers)
    response = await client.patch("/categories/9999", json=payload2, headers=admin_auth_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_category_partial(client,admin_auth_headers):
    payload1 = {
        "category_name": "test1",
    }
    payload2 = {}
    post_response = await client.post("/categories", json=payload1, headers=admin_auth_headers)
    category_id = post_response.json()["category_id"]
    response = await client.patch(f"/categories/{category_id}", json=payload2, headers=admin_auth_headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_category_success(client,admin_auth_headers):
    payload1 = {
        "category_name": "test1",
    }
    post_response = await client.post("/categories", json=payload1, headers=admin_auth_headers)
    category_id = post_response.json()["category_id"]
    response = await client.delete(f"/categories/{category_id}", headers=admin_auth_headers)
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_category_fail(client,admin_auth_headers):
    payload1 = {
        "category_name": "test1",
    }
    await client.post("/categories", json=payload1, headers=admin_auth_headers)
    response = await client.delete("/categories/9999", headers=admin_auth_headers)
    assert response.status_code == 404