import datetime
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from app.database import Base
from app.enums import RoleType

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False,unique=True)
    phone_number: Mapped[str] = mapped_column(nullable=False,unique=True)
    is_active: Mapped[bool] = mapped_column(default=True,nullable=False)
    role: Mapped[RoleType] = mapped_column(nullable=False)
    registration_date: Mapped[datetime.datetime] = mapped_column(default= lambda: datetime.datetime.now(datetime.UTC),nullable=False)
    cart: Mapped["Cart"] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")