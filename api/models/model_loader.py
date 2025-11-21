from ..dependencies.database import engine, Base

from .sandwiches import Sandwich
from .orders import Order
from .order_details import OrderDetail
from .recipes import Recipe
from .resources import Resource
from .customer import Customer
from .review import Review
from .payment import Payment
from .promotion import Promotion

__all__ = [
    "Sandwich",
    "Order",
    "OrderDetail",
    "Recipe",
    "Resource",
    "Customer",
    "Review",
    "Payment",
    "Promotion",
]

def index():
    Base.metadata.create_all(engine)