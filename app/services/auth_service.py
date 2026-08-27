from fastapi import HTTPException, status
from app.repositories import user_repository
from app.repositories.user_repository import UserRepository
from app.models.user_model import User
from app.enums import RoleType
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.auth_schema import Token
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token

class AuthService():
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        user_exist = await self.user_repo.get_by_email(user_data.email)
        if user_exist is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash= hash_password(user_data.password.get_secret_value()),
            email=user_data.email,
            phone_number=user_data.phone_number,
            role= RoleType.CUSTOMER,
            is_active=True)

        registered_user = await self.user_repo.create_user(new_user)
        return UserResponse.model_validate(registered_user)

    async def login_user(self, email: str, password: str) -> Token:
        user = await self.user_repo.get_by_email(email)

        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

        access_token = create_access_token(user_id= user.user_id, role= user.role)
        refresh_token = create_refresh_token(user_id= user.user_id)
        token = Token(access_token=access_token, refresh_token=refresh_token)
        return token
