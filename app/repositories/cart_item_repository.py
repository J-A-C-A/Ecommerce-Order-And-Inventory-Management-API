from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,  and_, delete
from app.models import CartItem

class CartItemRepository():
    def __init__(self, db: AsyncSession):
        self.db = db

    def add(self, new_item: CartItem) -> None:
        self.db.add(new_item)

    async def get_by_cart_and_product(self, cart_id: int, product_id: int) -> CartItem:
        query = select(CartItem).where( and_( CartItem.cart_id == cart_id, CartItem.product_id == product_id) )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_cart_item(self, new_item: CartItem) -> CartItem:
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return new_item

    async def update_cart_item(self, item: CartItem) -> CartItem:
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_cart_item(self, item: CartItem) -> None:
        await self.db.delete(item)
        await self.db.commit()

    async def delete_all_from_cart(self, cart_id: int) -> None:
        await self.db.execute(delete(CartItem).where(CartItem.cart_id == cart_id))
        await self.db.commit()

    async def delete_all_from_cart_without_commit(self, cart_id: int) -> None:
        await self.db.execute(delete(CartItem).where(CartItem.cart_id == cart_id))
