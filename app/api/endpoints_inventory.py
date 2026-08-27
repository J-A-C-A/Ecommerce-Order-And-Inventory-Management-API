from fastapi import APIRouter, Depends
from app.api.deps import get_inventory_service, get_current_admin_user
from app.models import User
from app.schemas.inventory_schema import InventoryAdminResponse, InventoryAdminUpdate
from app.services.inventory_service import InventoryService

router = APIRouter()

@router.get("/inventory/{product_id}")
async def get_inventory_by_product_id(product_id: int, inventory_serv: InventoryService = Depends(get_inventory_service), get_current_admin: User = Depends(get_current_admin_user)) -> InventoryAdminResponse:
    inventory = await inventory_serv.get_inventory(product_id)
    return inventory

@router.patch("/inventory/{product_id}")
async def update_inventory(product_id: int, inventory_to_update: InventoryAdminUpdate ,inventory_serv: InventoryService = Depends(get_inventory_service), get_current_admin: User = Depends(get_current_admin_user)) -> InventoryAdminResponse:
    inventory = await inventory_serv.update_inventory(product_id, inventory_to_update)
    return inventory
