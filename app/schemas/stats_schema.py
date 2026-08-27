import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.enums import OrderStatus
from app.schemas.product_schema import ProductResponse


class TopProductResponse(BaseModel):
    product: ProductResponse
    total_sold: int

class RevenueResponse(BaseModel):
    from_start: datetime.datetime
    to_end: datetime.datetime
    total_revenue: Decimal

class OrderCountByStatus(BaseModel):
    status: OrderStatus
    count: int