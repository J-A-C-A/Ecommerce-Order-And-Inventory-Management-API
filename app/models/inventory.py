import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from app.database import Base

class Inventory(Base):
    __tablename__ = "inventory"
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"),primary_key=True)
    quantity_total: Mapped[int] = mapped_column(nullable=False, default=0)
    quantity_reserved: Mapped[int] = mapped_column(nullable=False, default=0)
    updated_at: Mapped[datetime.datetime] = mapped_column(nullable=False, onupdate= lambda: datetime.datetime.now(datetime.UTC), default= lambda: datetime.datetime.now(datetime.UTC))
    product: Mapped["Product"] = relationship(back_populates="inventory")

    @property
    def quantity_available(self) -> int:
        return self.quantity_total - self.quantity_reserved