from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..dependencies.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255))
    discount_type = Column(String(20), nullable=False)  # percentage, fixed_amount
    discount_value = Column(Float, nullable=False)  # e.g., 20 for 20% or $20
    min_order_amount = Column(Float, default=0.0)
    max_discount_amount = Column(Float)  # Cap for percentage discounts
    usage_limit = Column(Integer)  # Total times code can be used
    usage_count = Column(Integer, default=0)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    start_date = Column(DateTime(timezone=True), nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    orders = relationship("OrderPromotion", back_populates="promotion")