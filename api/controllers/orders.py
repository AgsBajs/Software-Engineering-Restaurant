from datetime import datetime
from typing import List, Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.orders import Order
from ..models.order_details import OrderDetail
from ..models.sandwiches import Sandwich
from ..schemas.orders import (
    OrderCreate,
    OrderResponse,
    OrderItemCreate,
)


TAX_RATE = 0.07


def _get_sandwiches_by_id(db: Session, ids: List[int]) -> Dict[int, Sandwich]:
    if not ids:
        return {}

    sandwiches = db.query(Sandwich).filter(Sandwich.id.in_(ids)).all()
    return {s.id: s for s in sandwiches}


def create_order(db: Session, order_in: OrderCreate) -> Order:
    if not order_in.order_items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item.")

    for item in order_in.order_items:
        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid quantity {item.quantity} for menu item {item.menu_item_id}.",
            )

    sandwich_ids = [item.menu_item_id for item in order_in.order_items]
    sandwiches_by_id = _get_sandwiches_by_id(db, sandwich_ids)

    missing_ids = set(sandwich_ids) - set(sandwiches_by_id.keys())
    if missing_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Menu items not found: {sorted(missing_ids)}",
        )

    subtotal = 0.0
    order_details: List[OrderDetail] = []

    for item in order_in.order_items:
        sandwich = sandwiches_by_id[item.menu_item_id]
        unit_price = float(sandwich.price)
        line_subtotal = unit_price * item.quantity
        subtotal += line_subtotal

        detail = OrderDetail(
            sandwich_id=item.menu_item_id,
            amount=item.quantity,
            quantity=item.quantity,
            unit_price=unit_price,
            subtotal=line_subtotal,
            special_requests=item.special_requests,
        )
        order_details.append(detail)

    discount_amount = 0.0  # you can later plug in promo logic here
    tax_amount = round(subtotal * TAX_RATE, 2)
    total_price = subtotal + tax_amount - discount_amount

    tracking_number = f"TRK-{int(datetime.utcnow().timestamp())}"

    order = Order(
        customer_id=order_in.customer_id,
        delivery_address=order_in.delivery_address,
        special_instructions=order_in.special_instructions,
        tracking_number=tracking_number,
        order_status="PLACED",
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_price=total_price,
        order_date=datetime.utcnow(),
        estimated_delivery_time=None,
        actual_delivery_time=None,
        updated_at=None,
        promotion_code=order_in.promotion_code,
    )

    for detail in order_details:
        detail.order = order

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


def get_order_by_tracking(db: Session, tracking_number: str) -> Order:
    order = db.query(Order).filter(Order.tracking_number == tracking_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


def list_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    return db.query(Order).offset(skip).limit(limit).all()

def list_staff_orders(db: Session, skip: int = 0, limit: int = 1000) -> List[Order]:
    return list_orders(db, skip=skip, limit=limit)
