from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_name = Column(String(100), nullable=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    description = Column(String(255), nullable=True)

    order_details = relationship(
        "OrderDetail",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    payment = relationship("Payment", back_populates="order", cascade="all, delete-orphan")