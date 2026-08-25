from fastapi import HTTPException, status
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums import OrderStatus, ChangeAuthor
from app.models import Order, OrderItem, OrderStatusHistory
from app.repositories.order_repository import OrderRepository
from app.repositories.order_item_repository import OrderItemRepository
from app.repositories.order_status_history_repository import OrderStatusHistoryRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.order import OrderCreate, OrderResponse
from app.services.inventory_service import InventoryService
from app.services.cart_service import CartService


class OrderService():
    def __init__(self, db: AsyncSession, order_repository: OrderRepository, order_item_repository: OrderItemRepository, order_status_history_repository: OrderStatusHistoryRepository ,cart_repository: CartRepository, cart_item_repository: CartItemRepository, inventory_repository: InventoryRepository, inventory_service: InventoryService, cart_service: CartService) -> None:
        self.db = db
        self.order_repo = order_repository
        self.order_item_repo = order_item_repository
        self.order_status_history_repo = order_status_history_repository
        self.cart_repo = cart_repository
        self.cart_item_repo = cart_item_repository
        self.inventory_repo = inventory_repository
        self.inventory_serv = inventory_service
        self.cart_serv = cart_service

    async def create_order(self, user_id, order_data: OrderCreate) -> OrderResponse:
        cart = await self.cart_repo.get_by_user_id(user_id)
        if len(cart.cart_items) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items in cart")

        items_to_reserve = []
        for item in cart.cart_items:
            product_inventory = await self.inventory_repo.get_by_product_id(item.product_id)
            if product_inventory is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

            if product_inventory.quantity_available >= item.product_quantity:
                items_to_reserve.append(item)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail=f"Not enough reserved quantity of product {item.product_id} to release")

        new_order = Order(user_id= user_id,street=order_data.street,building_number=order_data.building_number,apartment_number=order_data.apartment_number, postal_code=order_data.postal_code,city=order_data.city,country=order_data.country)
        self.order_repo.add(new_order)
        await self.db.flush()

        for item in items_to_reserve:
            new_order_item = OrderItem(order_id=new_order.order_id, product_id=item.product_id,product_quantity=item.product_quantity, price=item.product.price)
            self.order_item_repo.add(new_order_item)
            await self.inventory_serv.reserve_stock_without_commit(new_order_item.product_id, new_order_item.product_quantity)
            new_history_record = OrderStatusHistory(order_id=new_order.order_id,status= OrderStatus.PENDING,change_by= ChangeAuthor.SYSTEM)
            self.order_status_history_repo.add(new_history_record)

        await self.cart_item_repo.delete_all_from_cart_without_commit(cart.cart_id)
        await self.db.commit()
        order = await self.order_repo.get_by_id(new_order.order_id)
        return OrderResponse.model_validate(order)
