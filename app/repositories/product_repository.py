from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.models.product_model import Product
from sqlalchemy.orm import selectinload
from decimal import Decimal

class ProductRepository():
    def __init__(self,db:AsyncSession):
        self.db = db

    def add(self, new_product: Product) -> None:
        self.db.add(new_product)

    async def get_by_id(self,product_id:int) -> Product | None:
        query = select(Product).options(selectinload(Product.category)).where(Product.product_id == product_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_product(self, new_product:Product) -> Product:
        self.db.add(new_product)
        await self.db.commit()
        product_with_category = await self.get_by_id(new_product.product_id)
        if product_with_category is None:
            raise NoResultFound(f"No product was found for product ID {new_product.product_id}")
        return product_with_category

    async def update_product(self, product:Product) -> Product:
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete_product(self,product: Product) -> None:
        await self.db.delete(product)
        await self.db.commit()

    async def search_product(self,
                             search: str | None = None,
                             is_active: bool | None = None,
                             min_price: Decimal | None = None,
                             max_price: Decimal | None = None,
                             category_id: int | None = None,
                             page: int = 1,
                             page_size: int = 20) -> tuple[list[Product],int]:
        query = select(Product).options(selectinload(Product.category))
        if search is not None:
            query = query.where( or_(Product.product_name.ilike(f"%{search}%"),
                                     Product.product_description.ilike(f"%{search}%"),) )

        if is_active is not None:
            query = query.where(Product.is_active == is_active)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
        if category_id is not None:
            query = query.where(Product.category_id == category_id)


        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = query.limit(page_size).offset( (page-1)* page_size)
        result = await self.db.execute(query)
        products = result.scalars().all()
        return (products,total)

