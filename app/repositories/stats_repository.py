from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal
from app.enums import OrderStatus
from app.models import Order, OrderItem


class StatsRepository():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_order_count_by_status(self) -> list[tuple[OrderStatus, int]]:
        query = select(Order.status, func.count(Order.order_id).label("count")).group_by(Order.status)
        result = await self.db.execute(query)
        rows = result.all()
        return [(row.status, row.count) for row in rows]

    async def get_revenue_by_period(self, start_date: datetime, end_date: datetime) -> Decimal:
        query = (
            select(func.sum(Order.total_price).label("revenue"))
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status.in_([OrderStatus.SHIPPED, OrderStatus.DELIVERED]))
        )
        result = await self.db.execute(query)
        scalar = result.scalar_one_or_none()
        value = scalar if scalar is not None else Decimal("0.00")
        return value

    async def get_best_selling_products(self, limit: int = 10) -> list[tuple[int, int]]:
        query = (select(OrderItem.product_id, func.sum(OrderItem.product_quantity).label("quantity"))
                 .join(Order, OrderItem.order_id == Order.order_id)
                 .where(Order.status.in_([OrderStatus.SHIPPED, OrderStatus.DELIVERED]))
                 .group_by(OrderItem.product_id)
                 .order_by(func.sum(OrderItem.product_quantity).desc())
                 .limit(limit))
        result = await self.db.execute(query)
        rows = result.all()
        return [(row.product_id,row.quantity) for row in rows]