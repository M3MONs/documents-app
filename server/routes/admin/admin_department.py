from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from core.roles import StaticRole
from services.department_service import DepartmentService
from core.security import RoleChecker, get_current_user
from core.database import get_db
from schemas.department import Department as DepartmentSchema, DepartmentCreatePayload


router = APIRouter(
    prefix="/admin/departments",
    tags=["admin_departments"],
    dependencies=[Depends(RoleChecker([StaticRole.DEPARTMENT_MANAGER.name_value]))],
)


@router.get("", response_model=PaginationResponse)
async def get_departments_paginated(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_user=Depends(get_current_user),
) -> PaginationResponse | None:
    organization_ids = await RoleChecker.get_user_organization_ids(
        db, current_user, [StaticRole.DEPARTMENT_MANAGER.name_value]
    )
    departments = await DepartmentService.get_paginated_departments(db, pagination, organization_ids=organization_ids)
    return departments


@router.get("/{department_id}", response_model=DepartmentSchema)
async def get_department_by_id(department_id: str, db: AsyncSession = Depends(get_db)) -> DepartmentSchema | None:
    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    RoleChecker([StaticRole.DEPARTMENT_MANAGER.name_value], org_param=str(department.organization_id))

    return DepartmentSchema.model_validate(department)


@router.delete("/{department_id}")
async def delete_department(department_id: str, db: AsyncSession = Depends(get_db)) -> None:
    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    RoleChecker([StaticRole.DEPARTMENT_MANAGER.name_value], org_param=str(department.organization_id))

    await DepartmentService.delete_department(db, department_id=department_id)


@router.post(
    "",
    response_model=DepartmentSchema,
    dependencies=[
        Depends(RoleChecker([StaticRole.DEPARTMENT_MANAGER.name_value], org_param="payload.organization_id"))
    ],
)
async def create_department(
    payload: DepartmentCreatePayload, db: AsyncSession = Depends(get_db)
) -> DepartmentSchema | None:
    if not await DepartmentService.is_department_name_unique_by_organization(db, payload.organization_id, payload.name):
        raise HTTPException(status_code=422, detail="Department name must be unique within the organization")

    created_department = await DepartmentService.create_department(db, payload)
    return DepartmentSchema.model_validate(created_department)


@router.put("/{department_id}")
async def update_department(
    department_id: str, payload: DepartmentCreatePayload, db: AsyncSession = Depends(get_db)
) -> None:
    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    RoleChecker([StaticRole.DEPARTMENT_MANAGER.name_value], org_param=str(department.organization_id))

    if not DepartmentService.validate_department_update(db, department_id, payload.name):
        raise HTTPException(status_code=400, detail="Department name must be unique")

    await DepartmentService.update_department(db, department_id=department_id, payload=payload)


@router.get(
    "/{department_id}/users",
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

    RoleChecker([StaticRole.DEPARTMENT_MANAGER.name_value], org_param=str(department.organization_id))

    users = await DepartmentService.get_paginated_users_with_assignment(db, department_id, pagination)

    return users


@router.post("/{department_id}/users/{user_id}/assign")
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


@router.post("/{department_id}/users/{user_id}/unassign")
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
