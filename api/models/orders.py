from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    customer_id = Column(Integer, nullable=False)  # 0 for guest orders
    delivery_address = Column(String(255), nullable=True)

    # we'll store guest metadata or notes here as JSON/text
    special_instructions = Column(Text, nullable=True)

    tracking_number = Column(String(50), unique=True, index=True, nullable=True)
    order_status = Column(String(50), nullable=False, default="PLACED")

    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, nullable=False, default=0.0)
    total_price = Column(Float, nullable=False)

    order_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    estimated_delivery_time = Column(DateTime, nullable=True)
    actual_delivery_time = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True, default=None)

    promotion_code = Column(String(50), nullable=True)

    order_details = relationship(
        "OrderDetail",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
    )