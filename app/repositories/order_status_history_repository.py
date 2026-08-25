from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import OrderStatusHistory

class OrderStatusHistoryRepository():
    def __init__(self, db: AsyncSession):
        self.db = db

    def add(self, history_entry: OrderStatusHistory) -> None:
        self.db.add(history_entry)

    async def get_all_for_order(self, order_id: int) -> list[OrderStatusHistory]:
        query = select(OrderStatusHistory).where(OrderStatusHistory.order_id == order_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_order_status_history(self, history_entry: OrderStatusHistory) -> OrderStatusHistory:
        self.db.add(history_entry)
        await self.db.commit()
        await self.db.refresh(history_entry)
        return history_entry