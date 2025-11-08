from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., ge=0)
    unit: str = Field(..., min_length=1, max_length=20)
    reorder_level: Optional[float] = Field(None, ge=0)


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    reorder_level: Optional[float] = Field(None, ge=0)


class IngredientResponse(IngredientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True