import uuid
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from core.roles import StaticRole
from services.user_service import UserService
from core.security import RoleChecker, get_current_user
from core.database import get_db
from schemas.user import PasswordResetPayload, UserEditPayload
from schemas.admin import UserAdmin as UserSchema


router = APIRouter(prefix="/admin/users", tags=["admin_users"], dependencies=[Depends(RoleChecker([StaticRole.USER_MANAGER.name_value]))])
    

@router.get("", response_model=PaginationResponse)
async def get_users_paginated(
    organization_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), pagination: PaginationParams = Depends()
) -> PaginationResponse:
    users = await UserService.get_paginated_users(db, pagination, organization_id)

    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> UserSchema | None:
    user = await UserService.get_user_by_id(db, user_id)
    if user:
        return UserSchema.model_validate(user)
    return None


# Deactivate user only for superuser
@router.delete("/{user_id}", dependencies=[Depends(RoleChecker([]))])
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active is False:
        raise HTTPException(status_code=400, detail="User is already deactivated")

    if user.is_superuser is True:
        raise HTTPException(status_code=403, detail="Cannot deactivate a superuser")

    await UserService.deactivate_user(db, user_id=user_id)


# Activate user only for superuser
@router.post("/{user_id}/activate", dependencies=[Depends(RoleChecker([]))])
async def activate_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active is True:
        raise HTTPException(status_code=400, detail="User is already activated")

    await UserService.activate_user(db, user_id=user_id)


# Reset user password only for superuser
@router.post("/{user_id}/reset-password", dependencies=[Depends(RoleChecker([]))])
async def reset_user_password(
    user_id: uuid.UUID,
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


@router.put("/{user_id}")
async def edit_user(
    user_id: uuid.UUID, payload: UserEditPayload, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
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
