from typing import List, Optional
from pydantic import BaseModel


class GuestOrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int
    special_requests: Optional[str] = None


class GuestOrderBase(BaseModel):
    guest_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    table_number: Optional[int] = None
    notes: Optional[str] = None
    promo_code: Optional[str] = None


class GuestOrderCreate(GuestOrderBase):
    items: List[GuestOrderItemCreate]
    promo_code: Optional[str] = None


class GuestOrderItem(BaseModel):
    id: int
    menu_item_id: int
    name: str
    quantity: int
    unit_price: float
    subtotal: float
    special_requests: Optional[str] = None

    class ConfigDict:
        from_attributes = True


class GuestOrder(GuestOrderBase):
    id: int
    code: str
    status: str
    subtotal: float
    total_price: float
    items: List[GuestOrderItem]
    promo_code: Optional[str] = None

    class ConfigDict:
        from_attributes = True
