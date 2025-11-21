from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies.database import get_db
from ..models.sandwiches import Sandwich
from ..schemas.menu_item import MenuItemCreate, MenuItemRead, MenuItemUpdate

router = APIRouter(prefix="/menu-items", tags=["Menu Items"])


@router.post("/", response_model=MenuItemRead, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
):
    item = Sandwich(**payload.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=List[MenuItemRead])
def list_menu_items(
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_vegetarian: Optional[bool] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(Sandwich)

    if not include_inactive:
        query = query.filter(Sandwich.is_active.is_(True))

    if search:
        pattern = f"%{search}%"
        query = query.filter(Sandwich.name.ilike(pattern))

    if category:
        query = query.filter(Sandwich.food_category == category)

    if is_vegetarian is not None:
        query = query.filter(Sandwich.is_vegetarian.is_(is_vegetarian))

    return query.all()


@router.get("/{item_id}", response_model=MenuItemRead)
def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = db.query(Sandwich).get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    return item


@router.put("/{item_id}", response_model=MenuItemRead)
def update_menu_item(
    item_id: int,
    payload: MenuItemUpdate,
    db: Session = Depends(get_db),
):
    item = db.query(Sandwich).get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(item, field, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = db.query(Sandwich).get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    db.delete(item)
    db.commit()
    return