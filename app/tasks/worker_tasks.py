from app.tasks.celery_app import celery_app
import time


@celery_app.task(name='send_order_email_task')
def send_order_email_task(order_id: int, user_id: int) -> str:
    time.sleep(10)
    return f'Order(id={order_id}) email has been sent to: {user_id}'