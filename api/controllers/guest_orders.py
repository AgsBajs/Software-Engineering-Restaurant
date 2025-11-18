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

    order_details: List[OrderDetail] = []
    for item in request.items:
        detail = OrderDetail(
            order_id=order.id,
            sandwich_id=item.menu_item_id,
            amount=item.quantity,
        )
        db.add(detail)
        order_details.append(detail)

    db.commit()
    db.refresh(order)

    response_items: List[GuestOrderItem] = []
    subtotal = 0.0

    for detail, item_req in zip(order_details, request.items):
        sandwich = sandwiches_by_id[detail.sandwich_id]
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
                special_requests=item_req.special_requests,
            )
        )

    total_price = subtotal

    order_code = f"ORD-{order.id:06d}"

    guest_order = GuestOrder(
        id=order.id,
        code=order_code,
        status="pending",
        subtotal=subtotal,
        total_price=total_price,
        items=response_items,
        guest_name=request.guest_name,
        contact_phone=request.contact_phone,
        contact_email=request.contact_email,
        table_number=request.table_number,
        notes=request.notes,
    )

    return guest_order

def _build_guest_order_response(order: Order) -> GuestOrder:
    items: List[GuestOrderItem] = []
    subtotal = 0.0

    for detail in order.order_details:
        sandwich = detail.sandwich
        if sandwich is None:
            continue

        unit_price = float(sandwich.price)
        quantity = detail.amount
        line_total = unit_price * quantity
        subtotal += line_total

        items.append(
            GuestOrderItem(
                id=detail.id,
                menu_item_id=sandwich.id,
                name=sandwich.sandwich_name,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=line_total,
                special_requests=None,
            )
        )

    code = f"ORD-{order.id:06d}"
    total_price = subtotal

    return GuestOrder(
        id=order.id,
        code=code,
        status="pending",
        subtotal=subtotal,
        total_price=total_price,
        items=items,
        guest_name=order.customer_name,
        contact_phone=None,
        contact_email=None,
        table_number=None,
        notes=order.description
    )

def read_one(db: Session, order_id: int) -> GuestOrder:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return _build_guest_order_response(order)
