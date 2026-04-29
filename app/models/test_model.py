import sqlalchemy as sa
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column

# id INTEGER PRIMARY KEY

class TestModel(Base):
    __tablename__ = 'test_models'  # название таблицы в базе данных

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


# alembic upgrade head
# alembic revision --autogenerate -m ""