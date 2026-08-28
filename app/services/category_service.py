from fastapi import HTTPException, status
from app.models import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category_schema import CategoryCreate, CategoryResponse, CategoryAdminUpdate
import json
from app.utils.cache import redis_client
class CategoryService():
    def __init__(self, category_repository: CategoryRepository):
        self.category_repo = category_repository

    async def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        category_exists = await self.category_repo.get_by_name(category_data.category_name)
        if category_exists is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
        new_category = Category(category_name=category_data.category_name)
        registered_category = await self.category_repo.create_category(new_category)
        await redis_client.delete("categories:all")
        return CategoryResponse.model_validate(registered_category)

    async def get_category(self, category_id: int) -> CategoryResponse:
        category = await self.category_repo.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return CategoryResponse.model_validate(category)

    async def update_category(self,category_id: int ,category_to_update: CategoryAdminUpdate) -> CategoryResponse:
        update_fields = category_to_update.model_dump(exclude_unset=True)
        category = await self.category_repo.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        for field_name, value in update_fields.items():
            setattr(category, field_name, value)
        updated_category = await self.category_repo.update_category(category)
        await redis_client.delete("categories:all")
        return CategoryResponse.model_validate(updated_category)

    async def delete_category(self, category_id: int) -> None:
        category = await self.category_repo.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        await self.category_repo.delete_category(category)
        await redis_client.delete("categories:all")

    async def get_all_categories(self) -> list[CategoryResponse]:
        cache_data = await redis_client.get("categories:all")
        if cache_data is not None:
            list_of_dicts = json.loads(cache_data)
            list_of_categories = [CategoryResponse(**dict_) for dict_ in list_of_dicts]
            return list_of_categories

        categories = await self.category_repo.get_all()
        result = [CategoryResponse.model_validate(category) for category in categories]
        list_of_dicts = [category.model_dump() for category in result]
        json_string = json.dumps(list_of_dicts,default=str)
        await redis_client.set("categories:all", json_string)
        return result
    