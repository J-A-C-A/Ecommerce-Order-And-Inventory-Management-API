from sqlalchemy.ext.asyncio import AsyncSession
from app.models import OrderItem


class OrderItemRepository():
    def __init__(self, db: AsyncSession):
        self.db = db

    def add(self, new_item: OrderItem) -> None:
        self.db.add(new_item)

    async def create_order_item(self, new_item: OrderItem) -> OrderItem:
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return new_item

    async def create_all(self, new_items: list[OrderItem]) -> list[OrderItem]:
        self.db.add_all(new_items)
        await self.db.commit()
        for item in new_items:
            await self.db.refresh(item)
        return new_items