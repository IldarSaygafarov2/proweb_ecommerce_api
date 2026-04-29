from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category

import sqlalchemy as sa


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self) -> list[Category]:
        """Получение всех категорий."""
        result = await self.session.execute(sa.select(Category).order_by(Category.id))
        return list(result.scalars().all())

    async def get(self, category_id: int) -> Category | None:
        """получение категории по id"""
        result = await self.session.execute(sa.select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def create(self, category: Category) -> Category:
        """создание записи в категории"""
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def update(self, category: Category) -> Category:
        """обновление категории"""
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        """удаление категории"""
        await self.session.delete(category)
        await self.session.commit()