from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cart_model import Cart
from app.models.cart_item_model import CartItem
from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart_schema import CartItemResponse, CartResponse, CartItemCreate, CartItemCustomerUpdate
from app.schemas.product_schema import ProductResponse
from decimal import Decimal


class CartService():
    def __init__(self, db: AsyncSession, cart_repository: CartRepository, cart_item_repository: CartItemRepository, product_repository: ProductRepository):
        self.db = db
        self.cart_repo = cart_repository
        self.cart_item_repo = cart_item_repository
        self.product_repo = product_repository

    async def _get_or_create_cart(self, user_id: int) -> Cart:
        cart = await self.cart_repo.get_by_user_id(user_id)
        if cart is None:
            new_cart = Cart(user_id=user_id, total_price= Decimal("0.00"))
            self.cart_repo.add(new_cart)
            await self.db.flush()
            return new_cart
        else:
            return cart

    async def _build_cart_response(self, cart: Cart) -> CartResponse:
        list_of_items = [CartItemResponse(product= ProductResponse.model_validate(item.product),
                                          product_quantity= item.product_quantity,
                                          total_item_price= item.product.price * item.product_quantity) for item in cart.cart_items]

        total_cart_price = sum(item.total_item_price for item in list_of_items)

        return CartResponse(total_cart_price=total_cart_price, cart_items= list_of_items)

    async def get_cart(self, user_id: int) -> CartResponse:
        await self._get_or_create_cart(user_id)
        await self.db.commit()
        cart = await self.cart_repo.get_by_user_id(user_id)
        return await self._build_cart_response(cart)

    async def add_item_to_cart(self, user_id: int ,new_cart_item_param: CartItemCreate) -> CartResponse:
        cart = await self._get_or_create_cart(user_id)
        product = await self.product_repo.get_by_id(new_cart_item_param.product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if not product.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is not active")

        existing_item = await self.cart_item_repo.get_by_cart_and_product(cart_id= cart.cart_id, product_id= product.product_id)
        if existing_item is None:
            new_cart_item = CartItem(product_id= new_cart_item_param.product_id, cart_id = cart.cart_id, product_quantity= new_cart_item_param.product_quantity)
            self.cart_item_repo.add(new_cart_item)
        else:
            existing_item.product_quantity += new_cart_item_param.product_quantity

        await self.db.commit()
        updated_cart = await self.cart_repo.get_by_user_id(user_id)
        return await self._build_cart_response(updated_cart)

    async def update_cart_item(self,user_id: int, product_id: int, update_data: CartItemCustomerUpdate) -> CartResponse:
        cart = await self._get_or_create_cart(user_id)
        item = await self.cart_item_repo.get_by_cart_and_product(cart_id= cart.cart_id, product_id= product_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        fields_to_update = update_data.model_dump(exclude_unset=True)
        for field,value in fields_to_update.items():
            setattr(item,field,value)
        updated_item = await self.cart_item_repo.update_cart_item(item=item)
        refreshed_cart = await self.cart_repo.get_by_user_id(user_id)
        return await self._build_cart_response(refreshed_cart)

    async def remove_item_from_cart(self,user_id: int, product_id: int) -> None:
        cart = await self._get_or_create_cart(user_id)
        item = await self.cart_item_repo.get_by_cart_and_product(cart_id= cart.cart_id,product_id= product_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        await self.cart_item_repo.delete_cart_item(item=item)

    async def remove_all_items_from_cart(self,user_id: int) -> None:
        cart = await self._get_or_create_cart(user_id)
        await self.cart_item_repo.delete_all_from_cart(cart_id= cart.cart_id)
