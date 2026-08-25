from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import InventoryAdminResponse, InventoryAdminUpdate


class InventoryService():
    def __init__(self,db: AsyncSession ,inventory_repository: InventoryRepository):
        self.db = db
        self.inventory_repo = inventory_repository

    async def get_inventory(self, product_id: int) -> InventoryAdminResponse:
        stack_for_product = await self.inventory_repo.get_by_product_id(product_id)
        return InventoryAdminResponse.model_validate(stack_for_product)

    async def update_inventory(self, product_id: int ,new_inventory: InventoryAdminUpdate) -> InventoryAdminResponse:
        product_to_update = await self.inventory_repo.get_by_product_id(product_id)
        if product_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        setattr(product_to_update,"quantity_total",new_inventory.quantity_total)
        await self.inventory_repo.update_item(product_to_update)
        return InventoryAdminResponse.model_validate(product_to_update)

    async def reserve_stock(self, product_id: int, quantity: int) -> None:
        product_inventory = await self.inventory_repo.get_by_product_id(product_id)

        if product_inventory is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        available_quantity = product_inventory.quantity_available

        if quantity > available_quantity:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Not enough quantity of product {product_id} to make reservation")

        product_inventory.quantity_reserved += quantity
        await self.inventory_repo.update_item(product_inventory)

    async def release_stock(self, product_id: int, quantity: int) -> None:
        product_inventory = await self.inventory_repo.get_by_product_id(product_id)

        if product_inventory is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        if quantity > product_inventory.quantity_reserved:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Not enough reserved quantity of product {product_id} to release")

        product_inventory.quantity_reserved -= quantity
        await self.inventory_repo.update_item(product_inventory)

    async def reserve_stock_without_commit(self, product_id: int, quantity: int) -> None:
        product_inventory = await self.inventory_repo.get_by_product_id(product_id)

        if product_inventory is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        available_quantity = product_inventory.quantity_available

        if quantity > available_quantity:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Not enough quantity of product {product_id} to make reservation")

        product_inventory.quantity_reserved += quantity
        self.inventory_repo.add(product_inventory)





