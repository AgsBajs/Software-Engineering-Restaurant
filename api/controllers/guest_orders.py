from uuid import uuid4
from datetime import datetime
from typing import List, Dict
import json

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


def _build_guest_order_response(db: Session, order: Order) -> GuestOrder:
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
        quantity = detail.quantity
        line_total = unit_price * quantity
        subtotal += line_total

        response_items.append(
            GuestOrderItem(
                id=detail.id,
                menu_item_id=sandwich.id,
                name=sandwich.name,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=line_total,
                special_requests=detail.special_requests,
            )
        )

    total_price = subtotal
    order_code = f"ORD-{order.id:06d}"

    guest_name = None
    contact_phone = None
    contact_email = None
    table_number = None
    notes = None

    if order.special_instructions:
        try:
            meta = json.loads(order.special_instructions)
            guest_name = meta.get("guest_name")
            contact_phone = meta.get("contact_phone")
            contact_email = meta.get("contact_email")
            table_number = meta.get("table_number")
            notes = meta.get("notes")
        except (ValueError, TypeError):
            notes = order.special_instructions

    return GuestOrder(
        id=order.id,
        code=order_code,
        status=order.order_status or "PENDING",
        subtotal=subtotal,
        total_price=total_price,
        items=response_items,
        guest_name=guest_name,
        contact_phone=contact_phone,
        contact_email=contact_email,
        table_number=table_number,
        notes=notes,
    )


def create(db: Session, request: GuestOrderCreate) -> GuestOrder:
    if not request.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item.")

    for item in request.items:
        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid quantity {item.quantity} for menu item {item.menu_item_id}.",
            )

    sandwich_ids = [item.menu_item_id for item in request.items]
    sandwiches_by_id = _get_sandwiches_by_id(db, sandwich_ids)
    missing_ids = set(sandwich_ids) - set(sandwiches_by_id.keys())
    if missing_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Sandwich IDs not found: {sorted(missing_ids)}",
        )

    subtotal = 0.0
    order_details: List[OrderDetail] = []

    for item in request.items:
        sandwich = sandwiches_by_id[item.menu_item_id]
        unit_price = float(sandwich.price)
        line_total = unit_price * item.quantity
        subtotal += line_total

        detail = OrderDetail(
            sandwich_id=item.menu_item_id,
            amount=item.quantity,
            quantity=item.quantity,
            unit_price=unit_price,
            subtotal=line_total,
            special_requests=item.special_requests,
        )
        order_details.append(detail)

    tax_amount = 0.07
    discount_amount = 0.0
    total_price = subtotal + tax_amount - discount_amount

    meta = {
        "guest_name": request.guest_name,
        "contact_phone": request.contact_phone,
        "contact_email": request.contact_email,
        "table_number": request.table_number,
        "notes": request.notes,
    }

    tracking_number = f"GUEST-{uuid4().hex[:0].upper()}"

    order = Order(
        customer_id=0,
        delivery_address=(
            f"Table {request.table_number}"
            if request.table_number is not None
            else "Guest order"
        ),
        special_instructions=json.dumps(meta),
        tracking_number=tracking_number,
        order_status="PENDING",
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_price=total_price,
        order_date=datetime.utcnow(),
        estimated_delivery_time=None,
        actual_delivery_time=None,
        updated_at=None,
        promotion_code=None,
    )

    for detail in order_details:
        detail.order = order

    db.add(order)
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
