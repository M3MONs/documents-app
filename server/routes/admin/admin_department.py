from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from services.department_service import DepartmentService
from core.security import RoleChecker
from core.database import get_db
from schemas.department import Department as DepartmentSchema


router = APIRouter(prefix="/admin/departments", tags=["admin_departments"])

@router.get("", dependencies=[Depends(RoleChecker(["admin"]))], response_model=PaginationResponse)
async def get_departments_paginated(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse:
    departments = await DepartmentService.get_paginated_departments(db, pagination.offset, pagination.page_size)
    return departments


@router.get("/{department_id}", dependencies=[Depends(RoleChecker(["admin"]))], response_model=DepartmentSchema)
async def get_department_by_id(department_id: str, db: AsyncSession = Depends(get_db)) -> DepartmentSchema | None:
    department = await DepartmentService.get_department_by_id(db, department_id)
    if department:
        return DepartmentSchema.model_validate(department)
    return None


@router.delete("/{department_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_department(department_id: str, db: AsyncSession = Depends(get_db)) -> None:
    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    await DepartmentService.delete_department(db, department_id=department_id)


class DepartmentCreatePayload(BaseModel):
    name: str = Field(..., description="The name for the new department")
    organization_id: str = Field(..., description="The ID of the organization the department belongs to")


@router.post("", dependencies=[Depends(RoleChecker(["admin"]))], response_model=DepartmentSchema)
async def create_department(
    payload: DepartmentCreatePayload, db: AsyncSession = Depends(get_db)
) -> DepartmentSchema | None:
    created_department = await DepartmentService.create_department(db, payload)
    return DepartmentSchema.model_validate(created_department)


@router.put("/{department_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_department(
    department_id: str, payload: DepartmentCreatePayload, db: AsyncSession = Depends(get_db)
) -> None:
    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if not DepartmentService.validate_department_update(db, department_id, payload.name):
        raise HTTPException(status_code=400, detail="Department name must be unique")

    await DepartmentService.update_department(db, department_id=department_id, payload=payload)


@router.get(
    "/{department_id}/users",
    dependencies=[Depends(RoleChecker(["admin"]))],
    response_model=PaginationResponse,
)
async def get_department_users_paginated(
    department_id: str,
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse:
    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    users = await DepartmentService.get_paginated_users_with_assignment(db, department_id, pagination)

    return users


@router.post("/{department_id}/users/{user_id}/assign", dependencies=[Depends(RoleChecker(["admin"]))])
async def assign_user_to_department(
    department_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    department = await DepartmentService.get_department_by_id(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    try:
        await DepartmentService.assign_user_to_department(db, user_id, department_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{department_id}/users/{user_id}/unassign", dependencies=[Depends(RoleChecker(["admin"]))]
)
async def unassign_user_from_department(
    department_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    department = await DepartmentService.get_department_by_id(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    try:
        await DepartmentService.unassign_user_from_department(db, user_id, department_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
