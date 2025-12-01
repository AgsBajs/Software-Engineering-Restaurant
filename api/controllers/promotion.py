from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.promotion import Promotion
from ..schemas.promotion import PromotionCreate, PromotionUpdate


def create_promotion(db: Session, promotion_in: PromotionCreate) -> Promotion:
    existing = (
        db.query(Promotion)
        .filter(Promotion.code == promotion_in.code)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A promotion with this code already exists.",
        )

    if promotion_in.expiration_date <= promotion_in.start_date:
        raise HTTPException(
            status_code=400,
            detail="expiration_date must be after start_date.",
        )

    promo = Promotion(
        code=promotion_in.code,
        description=promotion_in.description,
        discount_type=promotion_in.discount_type,
        discount_value=promotion_in.discount_value,
        min_order_amount=promotion_in.min_order_amount,
        max_discount_amount=promotion_in.max_discount_amount,
        usage_limit=promotion_in.usage_limit,
        is_active=promotion_in.is_active,
        start_date=promotion_in.start_date,
        expiration_date=promotion_in.expiration_date,
    )
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo


def list_promotions(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Promotion]:
    return (db.query(Promotion)
        .order_by(Promotion.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_promotion(db: Session, promotion_id: int) -> Promotion:
    promo = (
        db.query(Promotion)
        .filter(Promotion.id == promotion_id)
        .first()
    )
    if not promo:
        raise HTTPException(status_code=404, detail="Promotion not found.")
    return promo

def update_promotion(
    db: Session, promotion_id: int, promotion_in: PromotionUpdate
) -> Promotion:
    promo = get_promotion(db, promotion_id)

    data = promotion_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(promo, field, value)

    if promo.expiration_date <= promo.start_date:
        raise HTTPException(
            status_code=400,
            detail="expiration_date must be after start_date.",
        )

    db.commit()
    db.refresh(promo)
    return promo

def delete_promotion(db: Session, promotion_id: int) -> None:
    promo = get_promotion(db, promotion_id)
    db.delete(promo)
    db.commit()

def _ensure_promotion_active(promo: Promotion) -> None:
    now = datetime.utcnow()
    start = promo.start_date
    exp = promo.expiration_date

    if start is not None and start.tzinfo is not None:
        start = start.replace(tzinfo=None)

    if exp is not None and exp.tzinfo is not None:
        exp = exp.replace(tzinfo=None)

    if not promo.is_active:
        raise HTTPException(status_code=400, detail="Promotion is inactive.")

    if start is not None and start > now:
        raise HTTPException(
            status_code=400,
            detail="Promotion has not started yet.",
        )

    if exp is not None and exp < now:
        raise HTTPException(
            status_code=400,
            detail="Promotion has expired.",
        )

    if (
        promo.usage_limit is not None
        and promo.usage_count is not None
        and promo.usage_count >= promo.usage_limit
    ):
        raise HTTPException(
            status_code=400,
            detail="Promotion usage limit has been reached.",
        )

def get_promotion_by_code(
    db: Session, code: str, active_only: bool = True
) -> Promotion:
    promo = (
        db.query(Promotion)
        .filter(Promotion.code == code)
        .first()
    )

    if not promo:
        raise HTTPException(status_code=404, detail="Promotion code not found.")

    if active_only:
        _ensure_promotion_active(promo)

    return promo

def calculate_discount(promo: Promotion, order_subtotal: float) -> float:
    if order_subtotal < (promo.min_order_amount or 0.0):
        raise HTTPException(
            status_code=400,
            detail=f"Order subtotal must be at least {promo.min_order_amount} "
                   f"to use this promotion.",
        )

    if promo.discount_type == "percentage":
        discount = order_subtotal * (promo.discount_value / 100.0)
    else:
        discount = promo.discount_value

    if promo.max_discount_amount is not None:
        discount = min(discount, promo.max_discount_amount)

    discount = min(discount, order_subtotal)

    return round(discount, 2)

def increment_usage(promo: Promotion) -> None:
    if promo.usage_count is None:
        promo.usage_count = 0

    if promo.usage_limit is not None and promo.usage_count >= promo.usage_limit:
        raise HTTPException(
            status_code=400,
            detail="Promotion usage limit has been reached.",
        )

    promo.usage_count += 1

def validate_and_calculate_discount(
    db: Session,
    promo_code: Optional[str],
    order_subtotal: float,
) -> dict:

    if not promo_code or promo_code.strip() == "":
        return {
            "promo": None,
            "promo_code": None,
            "discount_amount": 0.0,
            "final_subtotal": round(order_subtotal, 2),
        }

    promo = get_promotion_by_code(db, promo_code, active_only=True)

    discount = calculate_discount(promo, order_subtotal)
    final_subtotal = max(order_subtotal - discount, 0,0)
    final_subtotal = round(final_subtotal, 2)

    increment_usage(promo)
    db.commit()
    db.refresh(promo)

    return {
        "promo": promo,
        "promo_code": promo.code,
        "discount_amount": discount,
        "final_subtotal": final_subtotal,
    }