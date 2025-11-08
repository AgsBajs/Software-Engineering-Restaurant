from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..dependencies.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    amount = Column(Float, nullable=False)  # Current stock amount
    unit = Column(String(20), nullable=False)  # e.g., kg, lbs, oz, pieces
    reorder_level = Column(Float)  # Minimum amount before reordering
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    menu_items = relationship("MenuItemIngredient", back_populates="ingredient")