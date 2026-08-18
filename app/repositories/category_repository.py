from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.category import Category

class CategoryRepository():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: int) -> Category | None:
        query = select(Category).where(Category.category_id == category_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, category_name: str) -> Category | None:
        query = select(Category).where(Category.category_name == category_name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Category]:
        query = select(Category).order_by(Category.category_name)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_category(self, new_category: Category) -> Category:
        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)
        return new_category

    async def update_category(self,  category: Category) -> Category:
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete_category(self, category: Category) -> None:
        await self.db.delete(category)
        await self.db.commit()
