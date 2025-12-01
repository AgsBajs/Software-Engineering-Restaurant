from typing import List

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.review import Review
from ..models.sandwiches import Sandwich
from ..schemas.review import ReviewResponse, RatingSummaryResponse


def list_reviews(db: Session, skip: int = 0, limit: int = 100) -> List[Review]:
    return (
        db.query(Review)
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def list_reviews_for_item(
    db: Session,
    menu_item_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[Review]:
    return (
        db.query(Review)
        .filter(Review.menu_item_id == menu_item_id)
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_rating_summary_for_item(db: Session, menu_item_id: int) -> RatingSummaryResponse:
    # Make sure the menu item exists
    exists = db.query(Sandwich).filter(Sandwich.id == menu_item_id).first()
    if not exists:
        raise HTTPException(status_code=404, detail=f"Menu item {menu_item_id} not found")

    avg_rating, count = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(Review.menu_item_id == menu_item_id)
        .one()
    )

    average = float(avg_rating) if avg_rating is not None else 0.0

    return RatingSummaryResponse(
        menu_item_id=menu_item_id,
        average_rating=average,
        review_count=count,
    )