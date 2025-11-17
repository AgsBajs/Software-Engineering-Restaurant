from typing import List, Optional
from pydantic import BaseModel, EmailStr
from .order_details import OrderDetail


class GuestOrderItemCreate(BaseModel):
    sandwich_id: int
    amount: int


class GuestOrderBase(BaseModel):
    guest_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    table_number: Optional[int] = None
    notes: Optional[str] = None


class GuestOrderCreate(GuestOrderBase):
    items: List[GuestOrderItemCreate]


class GuestOrder(GuestOrderBase):
    id: int
    code: str
    status: str
    items: List[OrderDetail]

    class ConfigDict:
        from_attributes = True