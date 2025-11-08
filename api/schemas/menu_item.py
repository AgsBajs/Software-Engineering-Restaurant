from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    calories: Optional[int] = Field(None, ge=0)
    food_category: str = Field(..., min_length=1, max_length=50)
    is_available: int = Field(default=1, ge=0, le=1)
    image_url: Optional[str] = Field(None, max_length=255)


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    calories: Optional[int] = Field(None, ge=0)
    food_category: Optional[str] = Field(None, min_length=1, max_length=50)
    is_available: Optional[int] = Field(None, ge=0, le=1)
    image_url: Optional[str] = Field(None, max_length=255)


class MenuItemResponse(MenuItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True