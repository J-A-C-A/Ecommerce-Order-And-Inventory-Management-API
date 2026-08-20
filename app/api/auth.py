from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_auth_service
from app.schemas.auth import Token
from app.schemas.user import UserResponse, UserCreate
from app.services.auth_service import AuthService
from fastapi import status
router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)) -> UserResponse:
    new_user = await auth_service.register_user(user_data)
    return new_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)) -> Token:
    user_token = await auth_service.login_user(form_data.username, form_data.password)
    return user_token

