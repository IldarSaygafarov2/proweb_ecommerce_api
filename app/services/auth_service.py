from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, create_access_token, create_refresh_token, verify_password
from app.models import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import UserCreate, TokenPair



class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def register(self, payload: UserCreate) -> User:
        if await self.user_repo.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email exists")

        user = User(
            email=payload.email,
            fullname=payload.fullname,
            hashed_password=hash_password(payload.password)
        )
        return await self.user_repo.create(user)
        # 24ildar03ildar


    async def login(self, email: str, password: str) -> TokenPair:  # TokenPair
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        return TokenPair(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id))
        )
