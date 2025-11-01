from fastapi import APIRouter, Depends, HTTPException
from core.security import RoleChecker
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from schemas.pagination import PaginationParams, PaginationResponse
from services.user_service import UserService


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", dependencies=[Depends(RoleChecker(["admin"]))], response_model=PaginationResponse)
async def get_users_paginated(
    db: AsyncSession = Depends(get_db),  pagination: PaginationParams = Depends()
) -> PaginationResponse:
    users = await UserService.get_paginated_users(db, pagination)

    return users


@router.delete("/users/{user_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)) -> None:
    user = await UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_active is False:
        raise HTTPException(status_code=400, detail="User is already deactivated")
    
    if user.is_superuser is True:
        raise HTTPException(status_code=403, detail="Cannot deactivate a superuser")
    
    await UserService.deactivate_user(db, user_id=user_id)
    

@router.post("/users/{user_id}/activate", dependencies=[Depends(RoleChecker(["admin"]))])
async def activate_user(user_id: str, db: AsyncSession = Depends(get_db)) -> None:
    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active is True:
        raise HTTPException(status_code=400, detail="User is already activated")

    await UserService.activate_user(db, user_id=user_id)