from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class ProductBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    image_url: str | None = None
    price: Decimal
    stock: int
    category_id: int


class ProductCreateSchema(ProductBaseSchema):
    pass

class ProductReadSchema(ProductBaseSchema):
    id: int
    slug: str


class ProductUpdateSchema(BaseModel):
    name: str |  None = None
    description: str | None = None
    image_url: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    category_id: int | None = None