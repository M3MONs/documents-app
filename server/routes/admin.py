from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from core.security import RoleChecker
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from schemas.pagination import PaginationParams, PaginationResponse
from services.user_service import UserService


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", dependencies=[Depends(RoleChecker(["admin"]))], response_model=PaginationResponse)
async def get_users_paginated(
    db: AsyncSession = Depends(get_db), pagination: PaginationParams = Depends()
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


class PasswordResetPayload(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=100, description="The new password for the user")


@router.post("/users/{user_id}/reset-password", dependencies=[Depends(RoleChecker(["admin"]))])
async def reset_user_password(user_id: str, payload: PasswordResetPayload, db: AsyncSession = Depends(get_db)) -> None:
    if not payload.new_password:
        raise HTTPException(status_code=400, detail="New password must be provided")

    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not bool(user.is_active):
        raise HTTPException(status_code=400, detail="Cannot reset password for an inactive user")
    
    if bool(user.is_superuser):
        raise HTTPException(status_code=403, detail="Cannot reset password for a superuser")
    

    await UserService.reset_user_password(db, user_id=user_id, new_password=payload.new_password)
