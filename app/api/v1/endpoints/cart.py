from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.cart import CartRead, CartItemUpsert
from app.services.cart_service import CartService

router = APIRouter(
    tags=['Cart']
)


@router.get('/')
async def get_cart(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> CartRead:
    return await CartService(db).get_cart(current_user.id)


@router.put('/items')
async def update_cart_items(
        payload: CartItemUpsert,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> CartRead:
    return await CartService(db).upsert_item(current_user.id, payload.product_id, payload.quantity)


@router.delete('/items/{product_id}')
async def remove_cart_item(
        product_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> CartRead:
    return await CartService(db).remove_item(current_user.id, product_id)


@router.delete('/')
async def clear_cart(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Response:
    await CartService(db).clear_cart(current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)