import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # get_by_id
    async def get_by_id(self, user_id: int) -> User | None:  # Optional[User]
        result = await self.session.execute(
            sa.select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    # get_by_email
    async def get_by_email(self, user_email: str) -> User | None:
        result = await self.session.execute(
            sa.select(User).where(User.email == user_email)
        )
        return result.scalar_one_or_none()

    # create
    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    # list_users
    async def list_users(self) -> list[User]:  # List[str] list[str]
        result = await self.session.execute(
            sa.select(User).order_by(User.id.desc())
        )
        return list(result.scalars().all())

