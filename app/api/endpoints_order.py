from fastapi import APIRouter, Depends
from app.models import User
from app.services.order_service import OrderService
from app.api.deps import get_current_user, get_current_admin_user, get_order_service
from app.schemas.order_schema import OrderCreate, OrderResponse, OrderStatusAdminUpdate

router = APIRouter()

@router.get("/orders")
async def get_all_orders_for_user(current_user: User = Depends(get_current_user), order_serv: OrderService = Depends(get_order_service)) -> list[OrderResponse]:
    orders = await order_serv.get_all_orders_for_user(current_user.user_id)
    return orders

@router.get("/orders/{order_id}")
async def get_order_by_id(order_id: int, order_serv: OrderService = Depends(get_order_service), current_user: User = Depends(get_current_user)) -> OrderResponse:
    order = await order_serv.get_order(current_user.user_id, order_id)
    return order

@router.patch("/orders/{order_id}/status")
async def update_order_status(order_id: int, status_data: OrderStatusAdminUpdate ,order_serv: OrderService = Depends(get_order_service), current_admin: User = Depends(get_current_admin_user)) -> OrderResponse:
    updated_order = await order_serv.update_order_status(order_id=order_id,status_data= status_data)
    return updated_order

@router.post("/orders/{order_id}/cancel", status_code=200)
async def cancel_order(order_id: int, current_user: User = Depends(get_current_user), order_serv: OrderService = Depends(get_order_service)) -> OrderResponse:
    updated_order = await order_serv.cancel_order(user_id=current_user.user_id, order_id= order_id)
    return updated_order

@router.post("/orders", status_code=201)
async def create_order(order_data: OrderCreate,current_user: User = Depends(get_current_user), order_serv: OrderService = Depends(get_order_service)) -> OrderResponse:
    new_order = await order_serv.create_order(user_id=current_user.user_id, order_data = order_data)
    return new_order