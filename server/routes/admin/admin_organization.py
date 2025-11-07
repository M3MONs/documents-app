from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from services.organization_service import OrganizationService
from services.user_service import UserService
from core.security import RoleChecker
from core.database import get_db
from schemas.organization import Organization as OrganizationSchema


router = APIRouter(prefix="/admin/organizations", tags=["admin_organizations"])

@router.get("", dependencies=[Depends(RoleChecker(["admin"]))], response_model=PaginationResponse)
async def get_organizations_paginated(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse:
    organizations = await OrganizationService.get_paginated_organizations(db, pagination)

    return organizations


@router.delete("/{organization_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_organization(organization_id: str, db: AsyncSession = Depends(get_db)) -> None:
    organization = await OrganizationService.get_organization_by_id(db, organization_id)

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    await OrganizationService.delete_organization(db, organization_id=organization_id)


class OrganizationEditPayload(BaseModel):
    name: str = Field(..., description="The new name for the organization")
    domain: str = Field("", description="The new domain for the organization")
    is_active: bool = Field(True, description="Whether the organization is active")


@router.put("/{organization_id}", dependencies=[Depends(RoleChecker(["admin"]))])
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
    domain: str | None = Field("", description="The domain for the new organization")
    is_active: bool = Field(True, description="Whether the organization is active")


@router.post("", dependencies=[Depends(RoleChecker(["admin"]))], response_model=OrganizationSchema)
async def create_organization(
    payload: OrganizationCreatePayload, db: AsyncSession = Depends(get_db)
) -> OrganizationSchema | None:
    if not await OrganizationService.is_unique_name(db, payload.name):
        raise HTTPException(status_code=400, detail="Organization name must be unique")

    if payload.domain == "":
        payload.domain = None

    if payload.domain and not await OrganizationService.is_unique_domain(db, payload.domain):
        raise HTTPException(status_code=400, detail="Organization domain must be unique")

    created_organization = await OrganizationService.create_organization(db, payload)
    return OrganizationSchema.model_validate(created_organization)


@router.get(
    "/{organization_id}/users",
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


@router.post("/{organization_id}/users/{user_id}/assign", dependencies=[Depends(RoleChecker(["admin"]))])
async def assign_user_to_organization(
    organization_id: str,
    user_id: str,
    payload: AssignUserPayload,
    db: AsyncSession = Depends(get_db),
) -> None:
    organization = await OrganizationService.get_organization_by_id(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await UserService.assign_user_to_organization(db, user_id, organization_id, set_primary=payload.set_primary)


@router.post(
    "/{organization_id}/users/{user_id}/unassign", dependencies=[Depends(RoleChecker(["admin"]))]
)
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