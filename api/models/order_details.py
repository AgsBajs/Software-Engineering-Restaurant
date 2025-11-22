from sqlalchemy import Column, ForeignKey, Integer, Float, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class OrderDetail(Base):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    sandwich_id = Column(Integer, ForeignKey("sandwiches.id"))
    amount = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    special_requests = Column(String(255), nullable=True)

    sandwich = relationship("Sandwich", back_populates="order_details")
    order = relationship("Order", back_populates="order_details")