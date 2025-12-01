from fastapi import Header, HTTPException, status
from typing import Optional, Callable, List
from ..schemas.roles import Role

def get_current_role(x_role: Optional[str] = Header(None)) -> Role:
    if x_role is None:
        return Role.CUSTOMER

    try:
        return Role(x_role.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {x_role}. Allowed: customer, staff, admin",
        )


def require_roles(*allowed_roles: Role) -> Callable:
    from fastapi import Depends  # local import to avoid circulars

    def _checker(role: Role = Depends(get_current_role)):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

    return _checker