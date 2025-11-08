from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    tracking_number = Column(String(50), unique=True, nullable=False, index=True)
    order_status = Column(String(20), nullable=False, default="pending")  # pending, confirmed, preparing, out_for_delivery, delivered, cancelled
    total_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    delivery_address = Column(String(255), nullable=False)
    special_instructions = Column(String(500))
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    estimated_delivery_time = Column(DateTime(timezone=True))
    actual_delivery_time = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    promotions = relationship("OrderPromotion", back_populates="order")
    payment = relationship("Payment", back_populates="order", uselist=False)