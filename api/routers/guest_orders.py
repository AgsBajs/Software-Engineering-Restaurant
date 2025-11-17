from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import guest_orders as controller
from ..schemas import guest_orders as schema
from ..dependencies.database import get_db

router = APIRouter(
    tags=["Guest Orders"],
    prefix="/guestorders"
)


@router.post(
    "/",
    response_model=schema.GuestOrder,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new guest order"
)
def create_guest_order(
    request: schema.GuestOrderCreate,
    db: Session = Depends(get_db)
):

    return controller.create(db=db, request=request)


@router.get(
    "/{order_id}",
    response_model=schema.GuestOrder,
    summary="Get a guest order by ID"
)
def get_guest_order(
    order_id: int,
    db: Session = Depends(get_db)
):

    return controller.read_one(db=db, order_id=order_id)


@router.get(
    "/lookup",
    response_model=schema.GuestOrder,
    summary="Lookup a guest order by public code"
)
def lookup_guest_order(
    code: str,
    db: Session = Depends(get_db)
):

    return controller.lookup_by_code(db=db, code=code)
