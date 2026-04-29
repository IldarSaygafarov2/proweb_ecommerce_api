from pydantic import BaseModel, ConfigDict


class CategoryBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None


class CategoryReadSchema(CategoryBaseSchema):
    id: int


class CategoryCreateSchema(CategoryBaseSchema):
    pass


class CategoryUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
