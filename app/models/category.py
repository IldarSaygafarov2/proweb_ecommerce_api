import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base



class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)

    products = relationship("Product", back_populates="category")