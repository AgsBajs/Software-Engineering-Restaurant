from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    rating: float = Field(..., ge=0, le=5)
    review_text: Optional[str] = Field(None, max_length=1000)


class ReviewCreate(ReviewBase):
    customer_id: int
    menu_item_id: int


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_text: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(ReviewBase):
    id: int
    customer_id: int
    menu_item_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RatingSummaryResponse(BaseModel):
    menu_item_id: int
    average_rating: float
    review_count: int