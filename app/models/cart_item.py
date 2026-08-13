from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from app.database import Base
from decimal import Decimal
from sqlalchemy import Numeric
from sqlalchemy import UniqueConstraint

class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("product_id", "cart_id"),)
    cart_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"),nullable=False)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.cart_id"),nullable=False)
    product_quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10,2),default=Decimal("0.00"),nullable=False)
    product: Mapped["Product"] = relationship( back_populates="cart_items")
    cart: Mapped["Cart"] = relationship(back_populates="cart_items")