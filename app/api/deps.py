from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums import RoleType
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.utils.security import decode_token
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db)

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        repo: UserRepository = Depends(get_user_repository),) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await repo.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleType.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Admin access required")
    return current_user

async def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repository=repo)