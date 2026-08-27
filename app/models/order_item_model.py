from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from app.database import Base
from decimal import Decimal
from sqlalchemy import Numeric
from sqlalchemy import UniqueConstraint

class OrderItem(Base):
    __tablename__ = 'order_items'
    __table_args__ = (UniqueConstraint('product_id', 'order_id'),)
    order_item_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.order_id'),nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.product_id'),nullable=False)
    product_quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10,2),default=Decimal("0.00"),nullable=False)
    order: Mapped["Order"] = relationship(back_populates="order_items")
    product: Mapped["Product"] = relationship(back_populates="order_items")