from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date,datetime,timezone,time
from app.repositories.stats_repository import StatsRepository
from app.schemas.stats import TopProductResponse, RevenueResponse, OrderCountByStatus
from app.services.product_service import ProductService


class StatsService():
    def __init__(self, db: AsyncSession, stats_repository: StatsRepository, product_service: ProductService):
        self.db = db
        self.stats_repo = stats_repository
        self.product_serv = product_service

    async def get_order_counts_by_status(self) -> list[OrderCountByStatus]:
        list_of_tuples = await self.stats_repo.get_order_count_by_status()
        result = [OrderCountByStatus(status= status,count= quantity) for status, quantity in list_of_tuples]
        return result

    async def get_revenue_by_period(self, start_date: date, end_date: date) -> RevenueResponse:
        start_datetime = datetime.combine(start_date,time.min,tzinfo=timezone.utc)
        end_datetime = datetime.combine(end_date,time.max,tzinfo=timezone.utc)
        revenue = await self.stats_repo.get_revenue_by_period(start_datetime, end_datetime)
        result = RevenueResponse(from_start=start_date, to_end=end_date,total_revenue=revenue)
        return result

    async def get_top_selling_products(self, limit: int = 10) -> list[TopProductResponse]:
        list_of_tuples = await self.stats_repo.get_best_selling_products(limit)
        list_of_products = [(await self.product_serv.get_product_by_id(product_id= product_id),quantity) for product_id, quantity in list_of_tuples]
        result = [TopProductResponse(product= product , total_sold= quantity) for product, quantity in list_of_products]
        return result
