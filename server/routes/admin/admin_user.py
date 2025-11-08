from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from services.user_service import UserService
from core.security import RoleChecker,get_current_user
from core.database import get_db
from schemas.user import User as UserSchema, PasswordResetPayload, UserEditPayload


router = APIRouter(prefix="/admin/users", tags=["admin_users"])


@router.get("", dependencies=[Depends(RoleChecker(["admin"]))], response_model=PaginationResponse)
async def get_users_paginated(
    organization_id: str | None = None, db: AsyncSession = Depends(get_db), pagination: PaginationParams = Depends()
) -> PaginationResponse:
    users = await UserService.get_paginated_users(db, pagination, organization_id)

    return users


@router.get("/{user_id}", dependencies=[Depends(RoleChecker(["admin"]))], response_model=UserSchema)
async def get_user_by_id(user_id: str, db: AsyncSession = Depends(get_db)) -> UserSchema | None:
    user = await UserService.get_user_by_id(db, user_id)
    if user:
        return UserSchema.model_validate(user)
    return None


@router.delete("/{user_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)) -> None:
    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active is False:
        raise HTTPException(status_code=400, detail="User is already deactivated")

    if user.is_superuser is True:
        raise HTTPException(status_code=403, detail="Cannot deactivate a superuser")

    await UserService.deactivate_user(db, user_id=user_id)


@router.post("/{user_id}/activate", dependencies=[Depends(RoleChecker(["admin"]))])
async def activate_user(user_id: str, db: AsyncSession = Depends(get_db)) -> None:
    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active is True:
        raise HTTPException(status_code=400, detail="User is already activated")

    await UserService.activate_user(db, user_id=user_id)


@router.post("/{user_id}/reset-password", dependencies=[Depends(RoleChecker(["admin"]))])
async def reset_user_password(
    user_id: str,
    payload: PasswordResetPayload,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> None:
    if not payload.new_password:
        raise HTTPException(status_code=400, detail="New password must be provided")

    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bool(user.is_active):
        raise HTTPException(status_code=400, detail="Cannot reset password for an inactive user")

    is_editing_self = str(current_user.id) == user_id
    if bool(user.is_superuser) and not is_editing_self:
        raise HTTPException(status_code=403, detail="Cannot reset password for a superuser")

    await UserService.reset_user_password(db, user_id=user_id, new_password=payload.new_password)


@router.put("/{user_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def edit_user(
    user_id: str, payload: UserEditPayload, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
) -> None:
    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bool(user.is_active):
        raise HTTPException(status_code=400, detail="Cannot edit an inactive user")

    is_editing_self = str(current_user.id) == user_id
    if bool(user.is_superuser) and not is_editing_self:
        raise HTTPException(status_code=403, detail="Cannot edit a superuser")

    await UserService.update_user(db, user_id=user_id, payload=payload)
