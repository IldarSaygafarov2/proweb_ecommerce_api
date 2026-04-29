from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class CartItemUpsert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int


class CartItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    price: Decimal
    line_total: Decimal



class CartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    items: list[CartItemRead]
    total_amount: Decimal
