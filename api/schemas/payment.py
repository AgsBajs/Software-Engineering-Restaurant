from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaymentBase(BaseModel):
    payment_type: str = Field(..., pattern="^(credit_card|debit_card|paypal|cash)$")
    card_type: Optional[str] = Field(None, max_length=20)


class PaymentCreate(PaymentBase):
    order_id: int
    amount: float = Field(..., gt=0)
    card_last_four: Optional[str] = Field(None, min_length=4, max_length=4)


class PaymentUpdate(BaseModel):
    transaction_status: Optional[str] = Field(None, pattern="^(pending|completed|failed|refunded)$")
    transaction_id: Optional[str] = Field(None, max_length=100)


class PaymentResponse(PaymentBase):
    id: int
    order_id: int
    transaction_status: str
    transaction_id: Optional[str] = None
    amount: float
    card_last_four: Optional[str] = None
    payment_date: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True