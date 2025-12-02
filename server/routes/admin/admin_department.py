import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from core.roles import StaticRole
from models.user import User
from repositories.user_repository import UserRepository
from services.organization_service import OrganizationService
from services.department_service import DepartmentService
from core.security import RoleChecker, get_current_user
from core.database import get_db
from schemas.department import Department as DepartmentSchema, DepartmentCreatePayload, DepartmentUpdatePayload


router = APIRouter(
    prefix="/admin/departments",
    tags=["admin_departments"],
)


async def verify_department_manager_access(db: AsyncSession, current_user: User, organization_id: uuid.UUID) -> None:
    if getattr(current_user, "is_superuser", False):
        return

    has_role = await UserRepository.user_has_role_in_organization(
        db,
        current_user.id, # type: ignore
        {StaticRole.DEPARTMENT_MANAGER.name_value},
        organization_id,  # type: ignore
    )
    if not has_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User lacks required role {StaticRole.DEPARTMENT_MANAGER.name_value} for this organization",
        )


@router.get("", response_model=PaginationResponse)
async def get_departments_paginated(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_user=Depends(get_current_user),
) -> PaginationResponse | None:
    organization_ids = await RoleChecker.get_user_organization_ids(db, current_user, [StaticRole.DEPARTMENT_MANAGER.name_value])
    departments = await DepartmentService.get_paginated_departments(db, pagination, organization_ids=organization_ids)
    return departments


@router.get("/organizations", dependencies=[Depends(RoleChecker([StaticRole.DEPARTMENT_MANAGER.name_value]))], response_model=PaginationResponse)
async def get_organizations_paginated(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
) -> PaginationResponse:
    organization_ids = await RoleChecker.get_user_organization_ids(db, current_user, [StaticRole.DEPARTMENT_MANAGER.name_value])
    organizations = await OrganizationService.get_paginated_organizations(db, pagination, organization_ids=organization_ids)

    return organizations


@router.get("/{department_id}", response_model=DepartmentSchema)
async def get_department_by_id(
    department_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DepartmentSchema | None:
    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    await verify_department_manager_access(db, current_user, department.organization_id)  # type: ignore

    return DepartmentSchema.model_validate(department)


@router.delete("/{department_id}")
async def delete_department(
    department_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    await verify_department_manager_access(db, current_user, department.organization_id)  # type: ignore

    await DepartmentService.delete_department(db, department_id=department_id)


@router.post("", response_model=DepartmentSchema)
async def create_department(
    payload: DepartmentCreatePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DepartmentSchema | None:
    await verify_department_manager_access(db, current_user, payload.organization_id)

    if not await DepartmentService.is_department_name_unique_by_organization(db, payload.organization_id, payload.name):
        raise HTTPException(status_code=422, detail="Department name must be unique within the organization")

    created_department = await DepartmentService.create_department(db, payload)
    return DepartmentSchema.model_validate(created_department)


@router.put("/{department_id}")
async def update_department(
    department_id: uuid.UUID,
    payload: DepartmentUpdatePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    await verify_department_manager_access(db, current_user, department.organization_id)  # type: ignore

    if not DepartmentService.validate_department_update(db, department_id, payload.name):
        raise HTTPException(status_code=400, detail="Department name must be unique")

    await DepartmentService.update_department(db, department_id=department_id, payload=payload)


@router.get(
    "/{department_id}/users",
    response_model=PaginationResponse,
)
async def get_department_users_paginated(
    department_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse:
    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    await verify_department_manager_access(db, current_user, department.organization_id)  # type: ignore

    users = await DepartmentService.get_paginated_users_with_assignment(db, department_id, pagination)

    return users


@router.post("/{department_id}/users/{user_id}/assign")
async def assign_user_to_department(
    department_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    department = await DepartmentService.get_department_by_id(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    await verify_department_manager_access(db, current_user, department.organization_id)  # type: ignore

    try:
        await DepartmentService.assign_user_to_department(db, user_id, department_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{department_id}/users/{user_id}/unassign")
async def unassign_user_from_department(
    department_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    department = await DepartmentService.get_department_by_id(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    await verify_department_manager_access(db, current_user, department.organization_id)  # type: ignore

    try:
        await DepartmentService.unassign_user_from_department(db, user_id, department_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
