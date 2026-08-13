import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.schemas.product import ProductResponse
from app.enums import OrderStatus, ChangeAuthor
from pydantic import ConfigDict
from typing import Optional

class OrderCreate(BaseModel):
    street: str
    building_number: str
    apartment_number: Optional[str] = None
    postal_code: str
    city: str
    country: str

class OrderItemResponse(BaseModel):
    order_item_id: int
    product: ProductResponse
    product_quantity: int
    total_item_price: Decimal
    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    order_id: int
    order_items: list[OrderItemResponse]
    status: OrderStatus
    order_date: datetime.datetime
    modified_date: datetime.datetime
    street: str
    building_number: str
    apartment_number: Optional[str] = None
    postal_code: str
    city: str
    country: str
    total_order_price: Decimal
    model_config = ConfigDict(from_attributes=True)

class OrderStatusAdminUpdate(BaseModel):
    status: OrderStatus
    note: Optional[str] = None

class OrderStatusHistoryResponse(BaseModel):
    order_id: int
    change_id: int
    status: OrderStatus
    change_at: datetime.datetime
    change_by: ChangeAuthor
    note: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


