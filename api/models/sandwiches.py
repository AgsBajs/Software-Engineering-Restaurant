from sqlalchemy import Column, Integer, String, Boolean, Numeric, Text
from sqlalchemy.orm import relationship
from ..dependencies.database import Base

class Sandwich(Base):
    __tablename__ = "sandwiches"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    ingredients_text = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    calories = Column(Integer, nullable=True)
    food_category = Column(String(50), nullable=True)

    is_vegetarian = Column(Boolean, nullable=False, default=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)

    order_details = relationship("OrderDetail", back_populates="sandwich", cascade="all, delete-orphan",)
    reviews = relationship("Review",back_populates="menu_item",cascade="all, delete-orphan",passive_deletes=True,)
    recipes = relationship("Recipe",back_populates="sandwich",cascade="all, delete-orphan",)