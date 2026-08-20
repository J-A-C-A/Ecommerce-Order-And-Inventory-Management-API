from fastapi import HTTPException, status
from app.models import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryAdminUpdate

class CategoryService():
    def __init__(self, category_repository: CategoryRepository):
        self.category_repo = category_repository

    async def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        category_exists = await self.category_repo.get_by_name(category_data.category_name)
        if category_exists is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
        new_category = Category(category_name=category_data.category_name)
        registered_category = await self.category_repo.create_category(new_category)
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
        return CategoryResponse.model_validate(updated_category)

    async def delete_category(self, category_id: int) -> None:
        category = await self.category_repo.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        await self.category_repo.delete_category(category)

    async def get_all_categories(self) -> list[CategoryResponse]:
        categories = await self.category_repo.get_all()
        return [CategoryResponse.model_validate(category) for category in categories]
    