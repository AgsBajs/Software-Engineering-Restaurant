from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class OrderPromotion(Base):
    __tablename__ = "order_promotions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False)
    discount_applied = Column(Float, nullable=False)  # Actual discount amount applied

    # Relationships
    order = relationship("Order", back_populates="promotions")
    promotion = relationship("Promotion", back_populates="orders")