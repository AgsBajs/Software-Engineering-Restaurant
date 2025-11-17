from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..schemas import guest_orders as schema


def create(db: Session, request: schema.GuestOrderCreate):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Guest order creation not implemented yet."
    )


def read_one(db: Session, order_id: int):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Guest order retrieval not implemented yet."
    )


def lookup_by_code(db: Session, code: str):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Guest order lookup not implemented yet."
    )
