"""
Model loader to import all models for SQLAlchemy to recognize them.
This ensures all tables are created when Base.metadata.create_all() is called.
"""

from .customer import Customer
from .menu_item import MenuItem
from .ingredient import Ingredient
from .menu_item_ingredient import MenuItemIngredient
from .orders import Order
from .order_item import OrderItem
from .promotion import Promotion
from .order_promotion import OrderPromotion
from .payment import Payment
from .review import Review

__all__ = [
    "Customer",
    "MenuItem",
    "Ingredient",
    "MenuItemIngredient",
    "Order",
    "OrderItem",
    "Promotion",
    "OrderPromotion",
    "Payment",
    "Review",
]