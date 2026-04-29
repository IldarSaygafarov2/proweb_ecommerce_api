from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    fullname: str | None = None
    password: str

# User

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)  #

    id: int
    email: EmailStr
    fullname: str | None = None
    role: UserRole


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class LoginData(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str
