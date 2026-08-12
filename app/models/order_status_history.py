import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from app.database import Base
from app.enums import OrderStatus, ChangeAuthor

class OrderStatusHistory(Base):
    __tablename__ = "order_status_histories"
    change_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"),nullable=False)
    status: Mapped[OrderStatus] = mapped_column(nullable=False)
    change_at: Mapped[datetime.datetime] = mapped_column(default=lambda: datetime.datetime.now(datetime.UTC),nullable=False)
    change_by: Mapped[ChangeAuthor] = mapped_column(default= ChangeAuthor.SYSTEM,nullable=False)
    note: Mapped[str] = mapped_column(nullable=True)
    order: Mapped["Order"] = relationship(back_populates="changes_history")
