from pydantic import BaseModel
from decimal import Decimal
from app.schemas.product_schema import ProductResponse
from pydantic import ConfigDict
from typing import Optional

class CartItemCreate(BaseModel):
    product_id: int
    product_quantity: int

class CartItemCustomerUpdate(BaseModel):
    product_quantity: Optional[int] = None

class CartItemResponse(BaseModel):
    product: ProductResponse
    product_quantity: int
    total_item_price: Decimal
    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    cart_items: list[CartItemResponse]
    total_cart_price: Decimal
    model_config = ConfigDict(from_attributes=True)