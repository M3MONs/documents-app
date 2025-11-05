from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from core.security import RoleChecker, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from schemas.pagination import PaginationParams, PaginationResponse
from services.organization_service import OrganizationService
from services.user_service import UserService
from schemas.organization import Organization as OrganizationSchema


router = APIRouter(prefix="/admin", tags=["admin"])

# region User Management Endpoints


@router.get("/users", dependencies=[Depends(RoleChecker(["admin"]))], response_model=PaginationResponse)
async def get_users_paginated(
    organization_id: str | None = None,
    db: AsyncSession = Depends(get_db), pagination: PaginationParams = Depends()
) -> PaginationResponse:
    users = await UserService.get_paginated_users(db, pagination, organization_id)

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


class UserEditPayload(BaseModel):
    email: str = Field(..., description="The new email for the user")


@router.put("/users/{user_id}", dependencies=[Depends(RoleChecker(["admin"]))])
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


# endregion User Management Endpoints

# region Organization Management Endpoints


@router.get("/organizations", response_model=PaginationResponse)
async def get_organizations_paginated(
    db: AsyncSession = Depends(get_db),
    dependencies=[Depends(RoleChecker(["admin"]))],
    pagination: PaginationParams = Depends(),
) -> PaginationResponse:
    organizations = await OrganizationService.get_paginated_organizations(db, pagination)

    return organizations


@router.delete("/organizations/{organization_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_organization(organization_id: str, db: AsyncSession = Depends(get_db)) -> None:
    organization = await OrganizationService.get_organization_by_id(db, organization_id)

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    await OrganizationService.delete_organization(db, organization_id=organization_id)


class OrganizationEditPayload(BaseModel):
    name: str = Field(..., description="The new name for the organization")
    domain: str = Field("", description="The new domain for the organization")
    is_active: bool = Field(True, description="Whether the organization is active")


@router.put("/organizations/{organization_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def edit_organization(
    organization_id: str, payload: OrganizationEditPayload, db: AsyncSession = Depends(get_db)
) -> None:
    organization = await OrganizationService.get_organization_by_id(db, organization_id)

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    if not bool(organization.is_active):
        raise HTTPException(status_code=400, detail="Cannot edit an inactive organization")

    await OrganizationService.update_organization(db, organization_id=organization_id, payload=payload)


class OrganizationCreatePayload(BaseModel):
    name: str = Field(..., description="The name for the new organization")
    domain: str = Field("", description="The domain for the new organization")
    is_active: bool = Field(True, description="Whether the organization is active")


@router.post("/organizations", dependencies=[Depends(RoleChecker(["admin"]))], response_model=OrganizationSchema)
async def create_organization(
    payload: OrganizationCreatePayload, db: AsyncSession = Depends(get_db)
) -> OrganizationSchema | None:
    if not await OrganizationService.is_unique_name(db, payload.name):
        raise HTTPException(status_code=400, detail="Organization name must be unique")

    if payload.domain and not await OrganizationService.is_unique_domain(db, payload.domain):
        raise HTTPException(status_code=400, detail="Organization domain must be unique")

    created_organization = await OrganizationService.create_organization(db, payload)
    return OrganizationSchema.model_validate(created_organization)


@router.get(
    "/organizations/{organization_id}/users",
    dependencies=[Depends(RoleChecker(["admin"]))],
    response_model=PaginationResponse,
)
async def get_organization_users_paginated(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse:
    organization = await OrganizationService.get_organization_by_id(db, organization_id)

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    users = await UserService.get_paginated_users(db, pagination, organization_id)

    return users


class AssignUserPayload(BaseModel):
    set_primary: bool = Field(False, description="Whether to set the organization as the user's primary organization")


@router.post("/organizations/{organization_id}/users/{user_id}/assign", dependencies=[Depends(RoleChecker(["admin"]))])
async def assign_user_to_organization(
    organization_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    payload: AssignUserPayload = Depends(AssignUserPayload),
) -> None:
    organization = await OrganizationService.get_organization_by_id(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await UserService.assign_user_to_organization(db, user_id, organization_id, set_primary=payload.set_primary)
    
@router.post("/organizations/{organization_id}/users/{user_id}/unassign", dependencies=[Depends(RoleChecker(["admin"]))])
async def unassign_user_from_organization(
    organization_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    organization = await OrganizationService.get_organization_by_id(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await UserService.unassign_user_from_organization(db, user_id, organization_id)

# endregion Organization Management Endpoints
