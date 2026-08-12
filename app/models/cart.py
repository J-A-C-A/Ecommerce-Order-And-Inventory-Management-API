from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from app.database import Base
from decimal import Decimal
from sqlalchemy import Numeric

class Cart(Base):
    __tablename__ = "carts"
    cart_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'),nullable=False, unique=True)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10,2),nullable=False, default=Decimal("0.00"))
    user: Mapped["User"] = relationship(back_populates="cart")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="cart")