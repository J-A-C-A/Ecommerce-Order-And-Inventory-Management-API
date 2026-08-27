from fastapi import APIRouter, Depends
from app.api.deps import get_product_service, get_current_admin_user
from app.models import User
from app.schemas.product_schema import ProductCreate, ProductAdminUpdate, ProductResponse, ProductListResponse
from app.services.product_service import ProductService
from decimal import Decimal

router = APIRouter()

@router.get("/products/{product_id}")
async def get_product(product_id: int, product_serv: ProductService = Depends(get_product_service)) -> ProductResponse:
    product = await product_serv.get_product_by_id(product_id)
    return product

@router.get("/products")
async def get_products(search: str | None = None,is_active: bool | None = None,min_price: Decimal | None = None,max_price: Decimal | None = None,category_id: int | None = None,page: int = 1,page_size: int = 20,product_serv: ProductService = Depends(get_product_service)) -> ProductListResponse:
    result = await product_serv.search_product(
                                         search=search,
                                         is_active= is_active,
                                         min_price= min_price,
                                         max_price= max_price,
                                         category_id= category_id,
                                         page= page,
                                         page_size= page_size)
    return result

@router.post("/products", status_code= 201)
async def create_product(product_data: ProductCreate,product_serv: ProductService = Depends(get_product_service),current_admin_user: User = Depends(get_current_admin_user)) -> ProductResponse:
    new_product = await product_serv.create_product(product_data)
    return new_product

@router.patch("/products/{product_id}")
async def update_product(product_id: int, product_data: ProductAdminUpdate ,product_serv: ProductService = Depends(get_product_service), current_admin_user: User = Depends(get_current_admin_user)) -> ProductResponse:
    updated_product = await product_serv.update_product(product_id, product_data)
    return updated_product

@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, product_serv: ProductService = Depends(get_product_service), current_admin_user: User = Depends(get_current_admin_user)) -> None:
    await product_serv.delete_product(product_id)