"""
Model loader to import all models for SQLAlchemy to recognize them.
This ensures all tables are created when Base.metadata.create_all() is called.
"""

from models.customer import Customer
from models.menu_item import MenuItem
from models.ingredient import Ingredient
from models.menu_item_ingredient import MenuItemIngredient
from models.order import Order
from models.order_item import OrderItem
from models.promotion import Promotion
from models.order_promotion import OrderPromotion
from models.payment import Payment
from models.review import Review

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