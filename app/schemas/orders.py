from decimal import Decimal
from pydantic import BaseModel,ConfigDict

from app.models.enums import OrderStatus


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    price: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    items: list[OrderItemRead]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
