from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Cart, CartItem, Product


class CartRepository():
    def __init__(self, db: AsyncSession):
        self.db = db

    def add(self, new_cart: Cart) -> None:
        self.db.add(new_cart)

    async def get_by_user_id(self, user_id: int) -> Cart | None:
        query = select(Cart).execution_options(populate_existing=True).options(selectinload(Cart.cart_items).selectinload(CartItem.product).selectinload(Product.category)).where(Cart.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_cart(self, new_cart: Cart) -> Cart:
        self.db.add(new_cart)
        await self.db.commit()
        await self.db.refresh(new_cart)
        return new_cart