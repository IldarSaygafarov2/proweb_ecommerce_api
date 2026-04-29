from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.orders import OrderRead, OrderItemRead
from app.repositories.cart_repo import CartRepository
from app.repositories.order_repo import OrderRepository
from app.repositories.products_repo import ProductRepository
from app.models.order import Order, OrderItem
from app.models.enums import OrderStatus

from app.tasks.worker_tasks import send_order_email_task


class OrderService:
    def __init__(self, session: AsyncSession):
        self.order_repo = OrderRepository(session)
        self.cart_repo = CartRepository(session)
        self.product_repo = ProductRepository(session)

    async def create_from_cart(self, user_id: int, background_tasks: BackgroundTasks) -> Order:
        cart = await self.cart_repo.get_or_create_for_user(user_id)
        if not cart.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cart is empty')

        total = 0
        order_items = []
        for item in cart.items:
            product = await self.product_repo.get(item.product_id)
            if not product:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f'Product {item.product_id} not found')

            line_price = product.price
            total += line_price * item.quantity
            order_items.append(
                OrderItem(product_id=item.product_id, quantity=item.quantity, price=line_price)
            )

        order = Order(
            user_id=user_id,
            total_amount=total,
            items=order_items,
            status=OrderStatus.pending
        )
        created = await self.order_repo.create(order)
        await self.cart_repo.clear_cart(cart.id)

        send_order_email_task.delay(created.id, user_id)

        return created

    async def list_orders(self, user_id: int | None = None) -> list[Order]:
        if user_id is None:
            return await self.order_repo.list_all()
        return await self.order_repo.list_for_user(user_id)

    async def update_status(self, order_id: int, status_payload: OrderStatus):
        order = await self.order_repo.get(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order not found')

        if order.status == OrderStatus.canceled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Order already canceled')

        order.status = status_payload
        return await self.order_repo.update(order)



def serialize_order(order: Order) -> OrderRead:
    return OrderRead(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        items=[
            OrderItemRead(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price
            )
            for item in order.items
        ]
    )