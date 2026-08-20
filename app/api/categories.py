from fastapi import APIRouter, Depends
from app.models.user import User
from app.api.deps import get_category_service, get_current_admin_user
from app.schemas.category import CategoryCreate, CategoryAdminUpdate
from app.services.category_service import CategoryService

router = APIRouter()

@router.get("/categories/{category_id}")
async def get_category(category_id: int,category_serv: CategoryService = Depends(get_category_service)):
    category = await category_serv.get_category(category_id=category_id)
    return category

@router.get("/categories")
async def get_categories(category_serv: CategoryService = Depends(get_category_service)):
    categories = await category_serv.get_all_categories()
    return categories

@router.post("/categories", status_code=201)
async def create_category(category_to_create: CategoryCreate,current_admin: User = Depends(get_current_admin_user),category_serve: CategoryService = Depends(get_category_service)):
    new_category = await category_serve.create_category(category_to_create)
    return new_category

@router.patch("/categories/{category_id}")
async def update_category(category_id: int,category_to_update: CategoryAdminUpdate, current_admin: User = Depends(get_current_admin_user),category_serv: CategoryService = Depends(get_category_service)):
    category = await category_serv.update_category(category_id, category_to_update)
    return category

@router.delete("/categories/{category_id}",status_code=204)
async def delete_category(category_id: int,current_admin: User = Depends(get_current_admin_user), category_serv: CategoryService = Depends(get_category_service)):
    await category_serv.delete_category(category_id)



