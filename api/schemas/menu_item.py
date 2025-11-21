from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import datetime


class MenuItemBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

    ingredients_text: Optional[str] = None
    price: condecimal(max_digits=10, decimal_places=2)

    calories: Optional[int] = None
    food_category: Optional[str] = Field(None, max_length=50)

    is_vegetarian: bool = False
    stock_quantity: int = 0
    is_active: bool = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

    ingredients_text: Optional[str] = None
    price: Optional[condecimal(max_digits=10, decimal_places=2)] = None

    calories: Optional[int] = None
    food_category: Optional[str] = Field(None, max_length=50)

    is_vegetarian: Optional[bool] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None


class MenuItemRead(MenuItemBase):
    id: int

    class Config:
        orm_mode = True