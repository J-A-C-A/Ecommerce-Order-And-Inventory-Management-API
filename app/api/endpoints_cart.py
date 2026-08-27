from fastapi import APIRouter, Depends
from app.api.deps import get_cart_service, get_current_user
from app.models import User
from app.schemas.cart_schema import CartResponse, CartItemCreate, CartItemCustomerUpdate
from app.services.cart_service import CartService

router = APIRouter()

@router.get("/cart")
async def get_cart(current_user: User = Depends(get_current_user), cart_serve: CartService = Depends(get_cart_service)) -> CartResponse:
    cart =  await cart_serve.get_cart(current_user.user_id)
    return cart

@router.post("/cart/items", status_code= 201)
async def add_item_to_cart(cart_item_param: CartItemCreate,current_user: User = Depends(get_current_user), cart_serv: CartService = Depends(get_cart_service)) -> CartResponse:
    cart = await cart_serv.add_item_to_cart(user_id= current_user.user_id, new_cart_item_param= cart_item_param)
    return cart

@router.patch("/cart/items/{product_id}")
async def update_cart_item(product_id: int,update_data: CartItemCustomerUpdate,current_user: User = Depends(get_current_user), cart_serv: CartService = Depends(get_cart_service)) -> CartResponse:
    cart = await cart_serv.update_cart_item(product_id= product_id,update_data= update_data, user_id = current_user.user_id)
    return cart

@router.delete("/cart/items/{product_id}", status_code=204)
async def remove_item_from_cart(product_id: int,current_user: User = Depends(get_current_user), cart_serv: CartService = Depends(get_cart_service)) -> None:
    await cart_serv.remove_item_from_cart(product_id= product_id,user_id=current_user.user_id)

@router.delete("/cart", status_code=204)
async def remove_all_items_from_cart(current_user: User = Depends(get_current_user),cart_serv: CartService = Depends(get_cart_service)) -> None:
    await cart_serv.remove_all_items_from_cart(user_id= current_user.user_id)

