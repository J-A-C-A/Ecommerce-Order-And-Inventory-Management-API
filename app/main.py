from fastapi import FastAPI
from app.api.health_check import router as health_router
from app.api.auth import router as auth_router
from app.api.categories import router as categories_router
from app.api.products import router as products_router
from app.api.inventory import router as inventory_router
from app.api.cart import router as cart_router
from app.api.order import router as order_router

app = FastAPI()
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(cart_router)
app.include_router(order_router)
#uvicorn app.main:app --reload