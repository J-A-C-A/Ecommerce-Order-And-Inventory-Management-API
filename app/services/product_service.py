import math
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Product, Inventory
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductAdminUpdate, ProductListResponse


class ProductService():
    def __init__(self, db: AsyncSession, product_repository: ProductRepository, inventory_repository: InventoryRepository):
        self.db = db
        self.product_repo = product_repository
        self.inventory_repo = inventory_repository

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        new_product = Product(product_name= product_data.product_name,
                              product_description= product_data.product_description,
                              is_active= product_data.is_active ,price= product_data.price,
                              category_id= product_data.category_id)
        self.product_repo.add(new_product)
        await self.db.flush()

        new_item_in_inventory = Inventory(product_id= new_product.product_id,quantity_total= product_data.initial_quantity)
        self.inventory_repo.add(new_item_in_inventory)
        await self.db.commit()
        await self.db.refresh(new_product)

        product_with_category = await self.product_repo.get_by_id(new_product.product_id)

        if product_with_category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")

        return ProductResponse.model_validate(product_with_category)

    async def get_product_by_id(self, product_id: int) -> ProductResponse:
        product = await self.product_repo.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
        return ProductResponse.model_validate(product)

    async def delete_product(self, product_id: int) -> None:
        product_to_delete = await self.product_repo.get_by_id(product_id)
        if product_to_delete is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
        product_to_delete.is_active = False
        await self.product_repo.update_product(product_to_delete)

    async def update_product(self, product_id: int, product_data: ProductAdminUpdate) -> ProductResponse:
        product_to_update = await self.product_repo.get_by_id(product_id=product_id)
        if product_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
        update_fields = product_data.model_dump(exclude_unset=True)
        for field,value in update_fields.items():
            setattr(product_to_update,field,value)

        updated_product = await self.product_repo.update_product(product_to_update)
        return ProductResponse.model_validate(updated_product)

    async def search_product(self,
                             search: str | None = None,
                             is_active: bool | None = None,
                             min_price: Decimal | None = None,
                             max_price: Decimal | None = None,
                             category_id: int | None = None,
                             page: int = 1,
                             page_size: int = 20
                             ) -> ProductListResponse:
        products, total = await self.product_repo.search_product(search=search,
                                                          is_active= is_active,
                                                          min_price= min_price,
                                                          max_price= max_price,
                                                          category_id= category_id,
                                                          page= page,
                                                          page_size= page_size)

        list_of_products = [ProductResponse.model_validate(p) for p in products]
        num_of_pages = math.ceil(total/page_size) if page_size > 0 else 0
        return ProductListResponse(products= list_of_products, total= total, page_size= page_size, number_of_pages= num_of_pages)
