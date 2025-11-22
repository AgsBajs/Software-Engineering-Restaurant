from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., gt=0)
    special_requests: Optional[str] = Field(None, max_length=255)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    delivery_address: str = Field(..., min_length=5, max_length=255)
    special_instructions: Optional[str] = Field(None, max_length=500)


class OrderCreate(OrderBase):
    customer_id: int
    order_items: List[OrderItemCreate]
    promotion_code: Optional[str] = None


class OrderUpdate(BaseModel):
    order_status: Optional[str] = Field(None, max_length=20)
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None


class OrderResponse(OrderBase):
    id: int
    customer_id: int
    tracking_number: str
    order_status: str
    total_price: float
    subtotal: float
    tax_amount: float
    discount_amount: float
    order_date: datetime
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    order_items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True