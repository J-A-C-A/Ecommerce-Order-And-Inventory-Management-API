from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Inventory


class InventoryRepository():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_product_id(self, product_id: int) -> Inventory | None:
        query = select(Inventory).where(Inventory.product_id == product_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_item(self, new_item: Inventory) -> Inventory:
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return new_item

    async def update_item(self, item: Inventory) -> Inventory:
        await self.db.commit()
        await self.db.refresh(item)
        return item