from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.enums import OrderStatus
from app.models import Order, OrderItem, Product
from datetime import datetime

class OrderRepository():
    def __init__(self, db: AsyncSession):
        self.db = db

    def add(self, new_order: Order) -> None:
        self.db.add(new_order)

    async def get_by_id(self, order_id: int) -> Order | None:
        query = select(Order).options(selectinload(Order.order_items).selectinload(OrderItem.product).selectinload(Product.category)).where(Order.order_id == order_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: int) -> list[Order]:
        query = select(Order).options(selectinload(Order.order_items).selectinload(OrderItem.product).selectinload(Product.category)).where(Order.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_order(self, new_order: Order) -> Order:
        self.db.add(new_order)
        await self.db.commit()
        await self.db.refresh(new_order)
        return new_order

    async def update_order(self, order: Order) -> Order:
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_pending_orders_older_than(self, cutoff_time: datetime) -> list[Order]:
        query = select(Order).options(selectinload(Order.order_items).selectinload(OrderItem.product).selectinload(Product.category)).where(Order.order_date < cutoff_time).where(Order.status == OrderStatus.PENDING)
        result = await self.db.execute(query)
        return result.scalars().all()