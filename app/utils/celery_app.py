import asyncio
from celery import Celery
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings
from app.utils.email import send_email

celery_app = Celery("ecommerce_tasks",broker=settings.CELERY_BROKER_URL)

celery_engine = create_async_engine(settings.DATABASE_URL,echo=True,poolclass=NullPool,)

CelerySession = async_sessionmaker(bind=celery_engine,expire_on_commit=False)

celery_app.conf.beat_schedule = {
    "cancel_expired_orders": {
        "task": "app.utils.celery_app.cancel_pending_orders_task",
        "schedule": 1800.0,
    }
}
@celery_app.task
def send_order_confirmation_email_task(order_id:int, email_address: str) -> None:
    subject = f"Confirmation e-mail for order {order_id}"
    body = f"Thank you for your order! We have received your order {order_id} and it has been successfully confirmed. We will process it shortly."
    asyncio.run(send_email(to_email=email_address,subject=subject, body=body))

async def cancel_pending_orders():
    from app.repositories.order_repository import OrderRepository
    from app.repositories.order_item_repository import OrderItemRepository
    from app.repositories.order_status_history_repository import OrderStatusHistoryRepository
    from app.repositories.cart_repository import CartRepository
    from app.repositories.user_repository import UserRepository
    from app.repositories.cart_item_repository import CartItemRepository
    from app.repositories.inventory_repository import InventoryRepository
    from app.repositories.product_repository import ProductRepository
    from app.services.inventory_service import InventoryService
    from app.services.cart_service import CartService
    from app.services.order_service import OrderService
    async with CelerySession() as db:
        order_repo = OrderRepository(db=db)
        order_item_repo = OrderItemRepository(db=db)
        order_status_history_repo = OrderStatusHistoryRepository(db=db)
        cart_repo = CartRepository(db=db)
        cart_item_repo = CartItemRepository(db=db)
        inventory_repo = InventoryRepository(db=db)
        user_repo = UserRepository(db=db)
        product_repo = ProductRepository(db=db)
        inventory_serv = InventoryService(db=db, inventory_repository=inventory_repo)
        cart_serv = CartService(db=db, cart_repository=cart_repo, cart_item_repository=cart_item_repo, product_repository=product_repo)
        order_serv = OrderService(db=db,
                                  order_repository=order_repo,
                                  order_item_repository=order_item_repo,
                                  order_status_history_repository=order_status_history_repo,
                                  cart_repository=cart_repo,
                                  cart_item_repository=cart_item_repo,
                                  inventory_repository=inventory_repo,
                                  user_repository=user_repo,
                                  inventory_service=inventory_serv,
                                  cart_service=cart_serv)
        canceled_orders = await order_serv.cancel_expired_orders()
        print(f"Canceled {canceled_orders} orders")

@celery_app.task
def cancel_pending_orders_task() -> None:
    asyncio.run(cancel_pending_orders())

#celery -A app.utils.celery_app.celery_app worker --loglevel=info --pool=solo
#celery -A app.utils.celery_app.celery_app beat --loglevel=info