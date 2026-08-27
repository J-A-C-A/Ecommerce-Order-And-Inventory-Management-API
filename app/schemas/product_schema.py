from pydantic import BaseModel
from decimal import Decimal
from app.schemas.category_schema import CategoryResponse
from pydantic import ConfigDict
from typing import Optional

class ProductCreate(BaseModel):
    product_name: str
    product_description: str
    is_active: bool
    price: Decimal
    category_id: int
    initial_quantity: int

class ProductResponse(BaseModel):
    product_id: int
    product_name: str
    product_description: str
    is_active: bool
    price: Decimal
    category: CategoryResponse
    model_config = ConfigDict(from_attributes=True)

class ProductAdminUpdate(BaseModel):
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    is_active: Optional[bool] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None

class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    number_of_pages: int
    page_size: int
    total: int

