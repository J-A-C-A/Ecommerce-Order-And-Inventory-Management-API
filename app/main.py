from fastapi import FastAPI
from app.api.health_check import router as health_router
from app.api.endpoints_auth import router as auth_router
from app.api.endpoints_category import router as categories_router
from app.api.endpoints_product import router as products_router
from app.api.endpoints_inventory import router as inventory_router
from app.api.endpoints_cart import router as cart_router
from app.api.endpoints_order import router as order_router
from app.api.endpoints_stats import router as stats_router

app = FastAPI()
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(stats_router)


#uvicorn app.main:app --reload
#celery -A app.utils.celery_app.celery_app worker --loglevel=info --pool=solo