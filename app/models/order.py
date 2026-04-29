from decimal import Decimal
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from .enums import OrderStatus


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"), index=True)
    status: Mapped[OrderStatus] = mapped_column(
        sa.Enum(OrderStatus, name='order_status', native_enum=False),
        default=OrderStatus.pending,
        nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(sa.ForeignKey("orders.id"), index=True)
    product_id: Mapped[int] = mapped_column(sa.ForeignKey("products.id"), index=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
