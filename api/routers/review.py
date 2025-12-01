from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..dependencies.database import get_db
from ..controllers import review as reviews_controller
from ..schemas.review import ReviewResponse, RatingSummaryResponse

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)

@router.get("/", response_model=List[ReviewResponse])
def list_reviews(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
                db: Session = Depends(get_db),
):
    return reviews_controller.list_reviews(db, skip=skip, limit=limit)


@router.get("/item/{menu_item_id}", response_model=List[ReviewResponse])
def list_reviews_for_item(menu_item_id: int, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
                        db: Session = Depends(get_db),
):
    return reviews_controller.list_reviews_for_item(db, menu_item_id=menu_item_id, skip=skip, limit=limit,)


@router.get("/item/{menu_item_id}/rating", response_model=RatingSummaryResponse)
def get_rating_summary(menu_item_id: int, db: Session = Depends(get_db),
):
    return reviews_controller.get_rating_summary_for_item(db, menu_item_id)