import sqlalchemy as sa
import enum

class UserRole(str, enum.Enum):
    admin = 'admin'
    customer = 'customer'


class OrderStatus(str, enum.Enum):
    pending = 'pending'
    shipped = 'shipped'
    canceled = 'canceled'
    paid = 'paid'
