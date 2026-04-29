from datetime import datetime

from pydantic import BaseModel, field_validator, ConfigDict


class ProductCommentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: str

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v.strip()


class ProductCommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    user_id: int
    user_email: str
    content: str
    created_at: datetime
