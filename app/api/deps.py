from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums import RoleType
from app.models.user import User
from app.repositories.category_repository import CategoryRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.services.inventory_service import InventoryService
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.utils.security import decode_token
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db)

async def get_category_repository(db: AsyncSession = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db=db)

async def get_product_repository(db: AsyncSession = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db=db)

async def get_inventory_repository(db: AsyncSession = Depends(get_db)) -> InventoryRepository:
    return InventoryRepository(db=db)

async def get_cart_repository(db: AsyncSession = Depends(get_db)) -> CartRepository:
    return CartRepository(db=db)

async def get_cart_item_repository(db: AsyncSession = Depends(get_db)) -> CartItemRepository:
    return CartItemRepository(db=db)

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

async def get_category_service(repo: CategoryRepository = Depends(get_category_repository)) -> CategoryService:
    return CategoryService(category_repository=repo)

async def get_product_service(db: AsyncSession = Depends(get_db), product_repository: ProductRepository = Depends(get_product_repository), inventory_repository: InventoryRepository = Depends(get_inventory_repository)) -> ProductService:
    return ProductService(db= db, product_repository=product_repository, inventory_repository=inventory_repository)

async def get_inventory_service(db: AsyncSession = Depends(get_db), inventory_repository: InventoryRepository = Depends(get_inventory_repository)) -> InventoryService:
    return InventoryService(db= db, inventory_repository=inventory_repository)

async def get_cart_service(db: AsyncSession = Depends(get_db), cart_repository: CartRepository = Depends(get_cart_repository), cart_item_repository: CartItemRepository = Depends(get_cart_item_repository), product_repository: ProductRepository = Depends(get_product_repository)) -> CartService:
    return CartService(db=db,cart_repository=cart_repository, cart_item_repository=cart_item_repository, product_repository=product_repository)