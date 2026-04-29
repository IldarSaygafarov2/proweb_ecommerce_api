from pydantic import BaseModel, ConfigDict

from app.models.enums import UserRole


class UserRoleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: UserRole
