from pydantic import BaseModel, ConfigDict
from app.enums import RoleType

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    role: RoleType
    exp: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str