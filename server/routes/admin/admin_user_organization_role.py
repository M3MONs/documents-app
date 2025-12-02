import asyncio
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.role_service import RoleService
from services.organization_service import OrganizationService
from services.user_service import UserService
from services.user_organization_role_service import UserOrganizationRoleService
from core.security import RoleChecker
from core.database import get_db
from schemas.user_organization_role import (
    UserOrganizationRole as UserOrganizationRoleSchema,
    UserOrganizationRoleCreatePayload,
    UserOrganizationRoleUpdatePayload,
)


router = APIRouter(
    prefix="/admin/user-organization-roles",
    tags=["admin_user_organization_roles"],
    dependencies=[Depends(RoleChecker([]))],
)


@router.get("/user/{user_id}", response_model=list[UserOrganizationRoleSchema])
async def get_user_organization_roles(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[UserOrganizationRoleSchema]:
    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    uors = await UserOrganizationRoleService.get_user_organization_roles(db, user_id)
    return [UserOrganizationRoleSchema.model_validate(uor) for uor in uors]


@router.get(
    "/user/{user_id}/organization/{organization_id}",
    response_model=list[UserOrganizationRoleSchema],
)
async def get_user_roles_in_organization(
    user_id: uuid.UUID, organization_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[UserOrganizationRoleSchema]:
    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    organization = await OrganizationService.get_organization_by_id(db, organization_id)

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    uors = await UserOrganizationRoleService.get_user_roles_in_organization(db, user_id, organization_id)
    return [UserOrganizationRoleSchema.model_validate(uor) for uor in uors]


@router.post("", response_model=UserOrganizationRoleSchema)
async def assign_role_to_user_in_organization(
    payload: UserOrganizationRoleCreatePayload, db: AsyncSession = Depends(get_db)
) -> UserOrganizationRoleSchema:
    user_task = UserService.get_user_by_id(db, payload.user_id)
    org_task = OrganizationService.get_organization_by_id(db, payload.organization_id)
    role_task = RoleService.get_role_by_id(db, payload.role_id)

    user, organization, role = await asyncio.gather(user_task, org_task, role_task)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    try:
        uor = await UserOrganizationRoleService.assign_role_to_user_in_organization(db, payload)
        return UserOrganizationRoleSchema.model_validate(uor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{uor_id}", response_model=UserOrganizationRoleSchema)
async def update_user_organization_role(
    uor_id: uuid.UUID, payload: UserOrganizationRoleUpdatePayload, db: AsyncSession = Depends(get_db)
) -> UserOrganizationRoleSchema:
    uor = UserOrganizationRoleService.get_by_id(db, uor_id)

    if not uor:
        raise HTTPException(status_code=404, detail="User organization role not found")

    updated_uor = await UserOrganizationRoleService.update_user_organization_role(db, uor_id, payload)
    if not updated_uor:
        raise HTTPException(status_code=404, detail="User organization role not found")
    return UserOrganizationRoleSchema.model_validate(updated_uor)


@router.delete("/{uor_id}")
async def remove_role_from_user_in_organization(uor_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    uor = await UserOrganizationRoleService.get_by_id(db, uor_id)

    if not uor:
        raise HTTPException(status_code=404, detail="User organization role not found")

    await UserOrganizationRoleService.remove_role_from_user_in_organization(db, uor_id)
