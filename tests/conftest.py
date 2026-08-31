import os
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text, update

os.environ["ENV_FILE"] = ".env.test"

from app.config import settings
from app.main import app
from app.database import get_db
from app.models.user_model import User
from app.enums import RoleType

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.execute(text("TRUNCATE TABLE cart_items, carts, categories, inventory, order_items, orders,order_status_histories, products,users RESTART IDENTITY CASCADE"))
        await session.commit()

    await engine.dispose()

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
    data = response.json()
    return {"email": payload["email"], "password": payload["password"], "user_id": data["user_id"]}

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
    data = response.json()
    return {"email": payload["email"], "password": payload["password"], "user_id": data["user_id"]}


@pytest_asyncio.fixture
async def customer_auth_headers(client, registered_customer):
    response = await client.post("/login", data= {"username": registered_customer["email"], "password": registered_customer["password"]})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def admin_auth_headers(client, registered_admin, db_session):
    await db_session.execute(
        update(User)
        .where(User.user_id == registered_admin["user_id"]).values(role= RoleType.ADMIN)
    )
    await db_session.commit()
    response = await client.post(
        "/login",
        data={"username": registered_admin["email"], "password": registered_admin["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}