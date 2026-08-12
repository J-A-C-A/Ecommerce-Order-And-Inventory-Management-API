from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from decimal import Decimal
from sqlalchemy import Numeric
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(nullable=False)
    product_description: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable= False,default=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10,2),nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"))
    category: Mapped["Category"] = relationship(back_populates="products")
