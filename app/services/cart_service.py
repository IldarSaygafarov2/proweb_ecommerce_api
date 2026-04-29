from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.cart import CartItem
from app.repositories.cart_repo import CartRepository
from app.repositories.products_repo import ProductRepository
from app.schemas.cart import CartRead


class CartService:
    def __init__(self, session: AsyncSession):
        self.cart_repo = CartRepository(session)
        self.product_repo = ProductRepository(session)

    async def get_cart(self, user_id: int) -> CartRead:
        cart = await self.cart_repo.get_or_create_for_user(user_id)
        return self._to_schema(cart)

    async def upsert_item(self, user_id: int, product_id: int, quantity: int) -> CartRead:
        if quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Quantity must be positive')

        cart = await self.cart_repo.get_or_create_for_user(user_id)
        product = await self.product_repo.get(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

        item = await self.cart_repo.get_item(cart.id, product_id)

        current_in_cart = item.quantity if item else 0
        new_total = current_in_cart + quantity
        if new_total > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Can not add more than in stock. In stock: {product.stock}. Requested: {new_total}'
            )
        product.stock -= quantity
        await self.product_repo.update(product)

        if item:
            item.quantity = new_total
            await self.cart_repo.update_item(item)
        else:
            await self.cart_repo.add_item(
                CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
            )
        return await self.get_cart(user_id)

    async def remove_item(self, user_id: int, product_id: int) -> CartRead:
        cart = await self.cart_repo.get_or_create_for_user(user_id)
        item = await self.cart_repo.get_item(cart.id, product_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')

        product = await self.product_repo.get(product_id)
        if product:
            product.stock += item.quantity
            await self.product_repo.update(product)
        await self.cart_repo.delete_item(cart.id, product_id)
        return await self.get_cart(user_id)

    async def clear_cart(self, user_id: int) -> None:
        cart = await self.cart_repo.get_or_create_for_user(user_id)
        for item in cart.items:
            item.product.stock += item.quantity
            await self.product_repo.update(item.product)
        await self.cart_repo.clear_cart(cart.id)


    @staticmethod
    def _to_schema(cart) -> CartRead:
        items = []
        total = Decimal('0')  # 0.0
        for item in cart.items:
            price = item.product.price
            line_total = price * item.quantity
            total += line_total
            items.append({
                'id': item.id,
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price': price,
                'line_total': line_total
            })
        print(items)
        return CartRead(id=cart.id, user_id=cart.user_id, items=items, total_amount=total)


