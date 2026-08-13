import datetime
from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional

class InventoryAdminUpdate(BaseModel):
    quantity_total: Optional[int] = None

class InventoryAdminResponse(BaseModel):
    product_id: int
    quantity_total: int
    quantity_reserved: int
    quantity_available: int
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)
