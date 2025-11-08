from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PromotionBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    discount_type: str = Field(..., pattern="^(percentage|fixed_amount)$")
    discount_value: float = Field(..., gt=0)
    min_order_amount: float = Field(default=0.0, ge=0)
    max_discount_amount: Optional[float] = Field(None, gt=0)
    usage_limit: Optional[int] = Field(None, gt=0)
    is_active: int = Field(default=1, ge=0, le=1)
    start_date: datetime
    expiration_date: datetime


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=255)
    discount_value: Optional[float] = Field(None, gt=0)
    min_order_amount: Optional[float] = Field(None, ge=0)
    max_discount_amount: Optional[float] = Field(None, gt=0)
    usage_limit: Optional[int] = Field(None, gt=0)
    is_active: Optional[int] = Field(None, ge=0, le=1)
    expiration_date: Optional[datetime] = None


class PromotionResponse(PromotionBase):
    id: int
    usage_count: int
    created_at: datetime

    class Config:
        from_attributes = True