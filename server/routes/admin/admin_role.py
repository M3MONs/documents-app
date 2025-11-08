from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from services.role_service import RoleService
from core.security import RoleChecker
from core.database import get_db
from schemas.role import RoleCreatePayload


router = APIRouter(prefix="/admin/roles", tags=["admin_roles"])


@router.get("", dependencies=[Depends(RoleChecker(["admin"]))], response_model=PaginationResponse)
async def get_roles_paginated(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse:
    roles = await RoleService.get_paginated_roles(db, pagination)
    return roles


@router.post("", dependencies=[Depends(RoleChecker(["admin"]))])
async def create_role(payload: RoleCreatePayload, db: AsyncSession = Depends(get_db)) -> None:
    is_unique = await RoleService.is_unique_name(db, payload.name)

    if not is_unique:
        raise HTTPException(status_code=400, detail="Role with this name already exists")

    await RoleService.create_role(db, payload)


@router.get("/{role_id}", dependencies=[Depends(RoleChecker(["admin"]))], response_model=RoleCreatePayload)
async def get_role_by_id(role_id: str, db: AsyncSession = Depends(get_db)) -> RoleCreatePayload | None:
    role = await RoleService.get_role_by_id(db, role_id)

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    return RoleCreatePayload.model_validate(role)


@router.delete("/{role_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)) -> None:
    role = await RoleService.get_role_by_id(db, role_id)

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    await RoleService.delete_role(db, role_id)
