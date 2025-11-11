from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from services.role_service import RoleService
from core.security import RoleChecker
from core.database import get_db
from schemas.role import RoleCreatePayload


router = APIRouter(prefix="/admin/roles", tags=["admin_roles"], dependencies=[Depends(RoleChecker([]))])


@router.get("", response_model=PaginationResponse)
async def get_roles_paginated(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse:
    roles = await RoleService.get_paginated_roles(db, pagination)
    return roles


@router.get("/{role_id}", response_model=RoleCreatePayload)
async def get_role_by_id(role_id: str, db: AsyncSession = Depends(get_db)) -> RoleCreatePayload | None:
    role = await RoleService.get_role_by_id(db, role_id)

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    return RoleCreatePayload.model_validate(role)