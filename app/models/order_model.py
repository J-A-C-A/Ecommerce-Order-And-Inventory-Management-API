import datetime
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from app.database import Base
from decimal import Decimal
from sqlalchemy import Numeric
from app.enums import OrderStatus

class Order(Base):
    __tablename__ = "orders"
    order_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"),nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10,2),default=Decimal("0.00"),nullable=False)
    status: Mapped[OrderStatus] = mapped_column(nullable=False,default=OrderStatus.PENDING)
    order_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),nullable=False, default= lambda: datetime.datetime.now(datetime.UTC))
    modification_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False,default= lambda: datetime.datetime.now(datetime.UTC) ,onupdate= lambda: datetime.datetime.now(datetime.UTC))
    street: Mapped[str] = mapped_column(nullable=False)
    building_number: Mapped[str] = mapped_column(nullable=False)
    apartment_number: Mapped[str] = mapped_column(nullable=True)
    postal_code: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(nullable=False)
    user: Mapped["User"] = relationship(back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
    changes_history: Mapped[list["OrderStatusHistory"]] = relationship(back_populates="order")


