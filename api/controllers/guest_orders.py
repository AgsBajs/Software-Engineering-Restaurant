from datetime import datetime
from typing import List, Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.orders import Order
from ..models.order_details import OrderDetail
from ..models.sandwiches import Sandwich
from ..schemas.guest_orders import (
    GuestOrderCreate,
    GuestOrder,
    GuestOrderItem,
)


def _get_sandwiches_by_id(db: Session, ids: List[int]) -> Dict[int, Sandwich]:
    if not ids:
        return {}

    sandwiches = db.query(Sandwich).filter(Sandwich.id.in_(ids)).all()
    return {s.id: s for s in sandwiches}


def _build_guest_order_response(
    db: Session,
    order: Order,
) -> GuestOrder:

    details: List[OrderDetail] = (
        db.query(OrderDetail)
        .filter(OrderDetail.order_id == order.id)
        .all()
    )

    if not details:
        raise HTTPException(
            status_code=404,
            detail=f"No order details found for order ID {order.id}",
        )

    sandwich_ids = [d.sandwich_id for d in details]
    sandwiches_by_id = _get_sandwiches_by_id(db, sandwich_ids)

    response_items: List[GuestOrderItem] = []
    subtotal = 0.0

    for detail in details:
        sandwich = sandwiches_by_id.get(detail.sandwich_id)
        if not sandwich:
            raise HTTPException(
                status_code=500,
                detail=f"Sandwich ID {detail.sandwich_id} referenced in order_details but not found.",
            )

        unit_price = float(sandwich.price)
        line_total = unit_price * detail.amount
        subtotal += line_total

        response_items.append(
            GuestOrderItem(
                id=detail.id,
                menu_item_id=sandwich.id,
                name=sandwich.sandwich_name,
                quantity=detail.amount,
                unit_price=unit_price,
                subtotal=line_total,
                # We don't store special_requests in the DB, so return None here.
                special_requests=None,
            )
        )

    total_price = subtotal
    order_code = f"ORD-{order.id:06d}"

    return GuestOrder(
        id=order.id,
        code=order_code,
        status="pending",
        subtotal=subtotal,
        total_price=total_price,
        items=response_items,
        guest_name=order.customer_name,
        contact_phone=None,
        contact_email=None,
        table_number=None,
        notes=order.description,
    )


def create(db: Session, request: GuestOrderCreate) -> GuestOrder:

    if not request.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item.")

    sandwich_ids = [item.menu_item_id for item in request.items]

    sandwiches_by_id = _get_sandwiches_by_id(db, sandwich_ids)
    missing_ids = set(sandwich_ids) - set(sandwiches_by_id.keys())
    if missing_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Sandwich IDs not found: {sorted(missing_ids)}",
        )

    order = Order(
        customer_name=request.guest_name or "Guest",
        order_date=datetime.utcnow(),
        description=request.notes,
    )
    db.add(order)
    db.flush()

    for item in request.items:
        detail = OrderDetail(
            order_id=order.id,
            sandwich_id=item.menu_item_id,
            amount=item.quantity,
        )
        db.add(detail)

    db.commit()
    db.refresh(order)

    return _build_guest_order_response(db, order)


def read_one(db: Session, order_id: int) -> GuestOrder:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")

    return _build_guest_order_response(db, order)


def lookup_by_code(db: Session, code: str) -> GuestOrder:
    prefix = "ORD-"
    if not code.startswith(prefix):
        raise HTTPException(status_code=400, detail="Invalid order code format")

    numeric_part = code[len(prefix):]

    if not numeric_part.isdigit():
        raise HTTPException(status_code=400, detail="Invalid order code format")

    order_id = int(numeric_part)
    return read_one(db, order_id)
