from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base


# Часы наручные
# chasy-naruchnie


# id
# name
# slug
# description
# image_url
# price
# stock
# category_id

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(200), index=True)
    slug: Mapped[str] = mapped_column(sa.String(250), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    image_url: Mapped[str] = mapped_column(sa.String(1024), nullable=True)
    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(default=0, nullable=False)
    category_id: Mapped[int] = mapped_column(sa.ForeignKey('categories.id'), index=True)

    category = relationship("Category", back_populates="products")
    comments = relationship("ProductComment", back_populates='product')
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class ProductComment(Base):
    __tablename__ = 'product_comments'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        sa.ForeignKey('products.id', ondelete='CASCADE'),
        index=True
    )
    user_id: Mapped[int] = mapped_column(sa.ForeignKey('users.id', ondelete='CASCADE'), index=True)
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(),
                                                 nullable=False)

    product = relationship("Product", back_populates='comments')
    user = relationship("User", back_populates="comments")

"""
category_id integer
"""