from fastapi import APIRouter, Depends
from app.models import User
from app.api.deps import get_stats_service, get_current_admin_user
from app.services.stats_service import StatsService
from app.schemas.stats import TopProductResponse, RevenueResponse, OrderCountByStatus
from datetime import date

router = APIRouter()

@router.get("/stats/count")
async def get_order_count_by_status(stats_serv: StatsService = Depends(get_stats_service),current_admin_user: User = Depends(get_current_admin_user)) -> list[OrderCountByStatus]:
    result = await stats_serv.get_order_counts_by_status()
    return result

@router.get("/stats/revenue")
async def get_revenue_by_period(start_date: date, end_date: date, stats_serv: StatsService = Depends(get_stats_service) ,current_admin_user: User = Depends(get_current_admin_user)) -> RevenueResponse:
    result = await stats_serv.get_revenue_by_period(start_date, end_date)
    return result

@router.get("/stats/top_products")
async def get_top_selling_products(limit: int = 10, stats_serv: StatsService =  Depends(get_stats_service), current_admin_user: User = Depends(get_current_admin_user)) -> list[TopProductResponse]:
    result = await stats_serv.get_top_selling_products(limit)
    return result