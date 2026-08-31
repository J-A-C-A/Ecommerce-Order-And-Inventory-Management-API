import pytest

@pytest.mark.asyncio
async def test_register_user_success(client):
    payload = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "email": "jan@example.com",
        "phone_number": "123456789",
        "password": "securepassword123",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jan@example.com"
    assert "password" not in data

@pytest.mark.asyncio
async def test_register_user_duplicate_fail(client,registered_customer):
    payload = {
        "first_name": "Jerzy",
        "last_name": "Urban",
        "email": registered_customer["email"],
        "phone_number": "777888999",
        "password": "somepassword",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_register_user_invalid_password(client):
    payload = {
        "first_name": "Michał",
        "last_name": "Probierz",
        "email": "michal@probierz.com",
        "phone_number": "333222111",
        "password": "123",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_user_missing_email(client):
    payload = {
        "first_name": "Czesław",
        "last_name": "Michniewicz",
        "phone_number": "711711711",
        "password": "aferapremiowa",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_success(client,registered_customer):
    response = await client.post("/login", data={"username": registered_customer["email"], "password": registered_customer["password"]})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client,registered_customer):
    response = await client.post("/login", data={"username": registered_customer["email"], "password": "wrongpassword"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    response = await client.post("/login", data={"username": "no@mail.com", "password": "nopassword"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client):
    response = await client.get("/cart")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_admin_endpoint_with_customer_token(client, customer_auth_headers):
    payload = {
        "category_name": "test",
    }
    response = await client.post("/categories",json=payload ,headers=customer_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(client):
    headers = {
        "Authorization": "Bearer invalid-token"
    }
    response = await client.get("/cart",headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_admin_endpoint_success(client, admin_auth_headers):
    payload = {
        "category_name": "test",
    }
    response = await client.post("/categories", json=payload, headers=admin_auth_headers)
    assert response.status_code == 201

