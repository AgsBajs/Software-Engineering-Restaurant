from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..dependencies.database import get_db
from ..schemas.orders import OrderCreate, OrderResponse
from ..controllers import orders as orders_controller

from ..dependencies.auth import require_roles
from ..schemas.roles import Role

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    order = orders_controller.create_order(db, order_in)
    return order


@router.get("/", response_model=List[OrderResponse])
def list_orders(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
                db: Session = Depends(get_db),):
    orders = orders_controller.list_orders(db, skip=skip, limit=limit)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = orders_controller.get_order(db, order_id)
    return order


@router.get("/tracking/{tracking_number}", response_model=OrderResponse)
def get_order_by_tracking(tracking_number: str, db: Session = Depends(get_db)):
    order = orders_controller.get_order_by_tracking(db, tracking_number)
    return order


@router.get("/staff", response_model=List[OrderResponse], summary="Staff view: list all orders",
            dependencies=[Depends(require_roles(Role.STAFF, Role.ADMIN))])
def list_staff_orders(skip: int = Query(0, ge=0), limit: int = Query(1000, ge=1, le=5000), db: Session = Depends(get_db)):
    orders = orders_controller.list_staff_orders(db, skip=skip, limit=limit)
    return orders

@router.get("/staff/{order_id}", response_model=OrderResponse, summary="Staff view: get any order by ID",
            dependencies=[Depends(require_roles(Role.STAFF, Role.ADMIN))],)
def get_order_for_staff(order_id: int, db: Session = Depends(get_db),):
    order = orders_controller.get_order(db, order_id)
    return order

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = orders_controller.get_order(db, order_id)
    return order