import os
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text, update
from sqlalchemy.pool import NullPool


os.environ["ENV_FILE"] = ".env.test"

from app.config import settings
from app.main import app
from app.database import get_db
from app.models.user_model import User
from app.enums import RoleType

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.execute(text("TRUNCATE TABLE cart_items, carts, categories, inventory, order_items, orders,order_status_histories, products,users RESTART IDENTITY CASCADE"))
        await session.commit()

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def registered_customer(client):
    payload = {
        "first_name": "Jan",
        "last_name": "Przykładowy",
        "email": "janprzyk@example.com",
        "phone_number": "111222333",
        "password": "password123",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    return {"email": payload["email"], "password": payload["password"], "user_id": data["user_id"]}

@pytest_asyncio.fixture
async def registered_second_customer(client):
    payload = {
        "first_name": "Piotr",
        "last_name": "Testowy",
        "email": "piotrtest@example.com",
        "phone_number": "999888777",
        "password": "password123",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    return { "email": payload["email"],"password": payload["password"],"user_id": data["user_id"]}


@pytest_asyncio.fixture
async def registered_admin(client):
    payload = {
        "first_name": "Jakub",
        "last_name": "Przykładowski",
        "email": "jakubprzyk@example.com",
        "phone_number": "444555666",
        "password": "password123",
    }
    response = await client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    return {"email": payload["email"],"password": payload["password"],"user_id": data["user_id"]}


@pytest_asyncio.fixture
async def customer_auth_headers(client, registered_customer):
    response = await client.post("/login", data= {"username": registered_customer["email"], "password": registered_customer["password"]})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def second_customer_auth_headers(client, registered_second_customer):
    response = await client.post("/login",data={"username": registered_second_customer["email"],"password": registered_second_customer["password"]})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def admin_auth_headers(client, registered_admin, db_session):
    await db_session.execute(update(User).where(User.user_id == registered_admin["user_id"]).values(role= RoleType.ADMIN))
    await db_session.commit()
    response = await client.post("/login",data={"username": registered_admin["email"], "password": registered_admin["password"]},)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def created_category(client, admin_auth_headers):
    response = await client.post("/categories", json={"category_name": "Electronics"}, headers=admin_auth_headers)
    return response.json()

@pytest_asyncio.fixture
async def created_product(client, admin_auth_headers,created_category):
    payload = {
        "product_name": "Test Product",
        "product_description": "Test Description",
        "is_active": True,
        "price": 10.00,
        "category_id": created_category["category_id"],
        "initial_quantity": 10,
    }
    response = await client.post("/products", json=payload, headers=admin_auth_headers)
    return response.json()

@pytest_asyncio.fixture
async def created_cart_with_item(client, customer_auth_headers,created_product):
    payload = {"product_id": created_product["product_id"], "product_quantity": 2}
    response = await client.post("/cart/items", json=payload, headers=customer_auth_headers)
    return {"product": created_product, "cart": response.json()}

@pytest_asyncio.fixture
async def shipped_order(client,created_product,customer_auth_headers,admin_auth_headers):
    cart_response = await client.post("/cart/items",json={"product_id": created_product["product_id"],"product_quantity": 2},headers=customer_auth_headers)
    assert cart_response.status_code == 201
    payload = {
        "street": "Testowa",
        "building_number": "1",
        "apartment_number": "1",
        "postal_code": "01-001",
        "city": "Testowe",
        "country": "Testlandia",}
    order_response = await client.post("/orders",json=payload,headers=customer_auth_headers)
    assert order_response.status_code == 201

    order = order_response.json()
    order_id = order["order_id"]

    paid_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Paid"},headers=admin_auth_headers)
    assert paid_response.status_code == 200

    shipped_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Shipped"},headers=admin_auth_headers)
    assert shipped_response.status_code == 200

    return {"order": order,"product": created_product}


@pytest_asyncio.fixture
async def delivered_order(client,created_product,customer_auth_headers,admin_auth_headers):
    cart_response = await client.post("/cart/items",json={"product_id": created_product["product_id"],"product_quantity": 2},headers=customer_auth_headers)
    assert cart_response.status_code == 201
    payload = {
        "street": "Testowa",
        "building_number": "2",
        "apartment_number": "2",
        "postal_code": "02-002",
        "city": "Testowe",
        "country": "Testlandia",}

    order_response = await client.post("/orders",json=payload,headers=customer_auth_headers)
    assert order_response.status_code == 201

    order = order_response.json()
    order_id = order["order_id"]

    paid_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Paid"},headers=admin_auth_headers)
    assert paid_response.status_code == 200

    shipped_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Shipped"},headers=admin_auth_headers)
    assert shipped_response.status_code == 200

    delivered_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Delivered"},headers=admin_auth_headers)
    assert delivered_response.status_code == 200

    return {"order": order,"product": created_product}