import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .enums import UserRole

from app.db.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(sa.String(150), index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(sa.String(255))
    fullname: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole, name='user_role', native_enum=False),
        default=UserRole.customer,
        nullable=False
    )

    comments = relationship("ProductComment", back_populates="user")
    cart = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")


# related_name

# id
# email
# hashed_password
# fullname
# role
