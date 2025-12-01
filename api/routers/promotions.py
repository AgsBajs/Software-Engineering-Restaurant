from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..dependencies.database import get_db
from ..dependencies.auth import require_roles
from ..schemas.roles import Role
from ..schemas.promotion import PromotionCreate, PromotionUpdate, PromotionResponse
from ..controllers import promotion as promotion_controller

router = APIRouter(
    prefix="/promotions",
    tags=["Promotions"],
)

@router.post(
    "/",
    response_model=PromotionResponse,
    status_code=201,
    dependencies=[Depends(require_roles(Role.STAFF, Role.ADMIN))],
)
def create_promotion(
    promotion_in: PromotionCreate,
    db: Session = Depends(get_db),
):
    return promotion_controller.create_promotion(db, promotion_in)

@router.get(
    "/",
    response_model=List[PromotionResponse],
    dependencies=[Depends(require_roles(Role.STAFF, Role.ADMIN))],
)
def list_promotions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return promotion_controller.list_promotions(db, skip=skip, limit=limit)

@router.get(
    "/{promotion_id}",
    response_model=PromotionResponse,
    dependencies=[Depends(require_roles(Role.STAFF, Role.ADMIN))],
)
def get_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
):
    return promotion_controller.get_promotion(db, promotion_id)

@router.patch(
    "/{promotion_id}",
    response_model=PromotionResponse,
    dependencies=[Depends(require_roles(Role.STAFF, Role.ADMIN))],
)
def update_promotion(
    promotion_id: int,
    promotion_in: PromotionUpdate,
    db: Session = Depends(get_db),
):
    return promotion_controller.update_promotion(db, promotion_id, promotion_in)


@router.delete(
    "/{promotion_id}",
    status_code=204,
    dependencies=[Depends(require_roles(Role.STAFF, Role.ADMIN))],
)
def delete_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
):
    promotion_controller.delete_promotion(db, promotion_id)