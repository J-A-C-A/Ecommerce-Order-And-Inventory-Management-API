import datetime
from pydantic import BaseModel, EmailStr, SecretStr, field_validator
from app.enums import RoleType
from pydantic import ConfigDict
from typing import Optional

def validate_password(cls,value: SecretStr) -> SecretStr:
    if value is None:
        return value
    password = value.get_secret_value()
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    return value

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    password: SecretStr
    email: EmailStr
    phone_number: str
    _validate_password = field_validator("password")(validate_password)

class UserResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    is_active: bool
    registration_date: datetime.datetime
    model_config = ConfigDict(from_attributes= True)

class UserAdminUpdate(BaseModel):
    user_id: Optional[int] = None
    password: Optional[SecretStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[RoleType] = None
    registration_date: Optional[datetime.datetime] = None
    _validate_password = field_validator("password")(validate_password)

