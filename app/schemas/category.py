from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional

class CategoryCreate(BaseModel):
    category_name: str

class CategoryResponse(BaseModel):
    category_id: int
    category_name: str
    model_config = ConfigDict(from_attributes=True)

class CategoryAdminUpdate(BaseModel):
    category_id: Optional[int] = None
    category_name: Optional[str] = None
