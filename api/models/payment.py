from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..dependencies.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    payment_type = Column(String(20), nullable=False)  # credit_card, debit_card, paypal, cash
    transaction_status = Column(String(20), nullable=False, default="pending")  # pending, completed, failed, refunded
    transaction_id = Column(String(100), unique=True, index=True)
    amount = Column(Float, nullable=False)
    card_last_four = Column(String(4))  # Last 4 digits of card
    card_type = Column(String(20))  # visa, mastercard, amex, etc.
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="payment")