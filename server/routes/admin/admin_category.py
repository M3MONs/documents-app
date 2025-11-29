from fastapi import APIRouter, Depends, HTTPException, status
from core.roles import StaticRole
from core.security import RoleChecker, get_current_user
from core.database import get_db
from models.user import User
from repositories.user_repository import UserRepository
from schemas.category import CategoryCreatePayload, CategoryUpdatePayload
from schemas.pagination import PaginationParams
from schemas.pagination import PaginationResponse
from services.sync_service import SyncService
from services.organization_service import OrganizationService
from services.category_service import CategoryService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/admin/categories",
    tags=["admin_categories"],
)


async def verify_category_manager_access(
    db: AsyncSession, current_user: User, organization_id: str
) -> None:
    if getattr(current_user, "is_superuser", False):
        return

    has_role = await UserRepository.user_has_role_in_organization(
        db, str(current_user.id), {StaticRole.CATEGORIES_MANAGER.name_value}, organization_id
    )
    if not has_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User lacks required role {StaticRole.CATEGORIES_MANAGER.name_value} for this organization",
        )


@router.get("", response_model=PaginationResponse)
async def get_categories_paginated(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_user=Depends(get_current_user),
) -> PaginationResponse | None:
    organization_ids = await RoleChecker.get_user_organization_ids(
        db, current_user, [StaticRole.DEPARTMENT_MANAGER.name_value]
    )
    categories = await CategoryService.get_paginated_categories(db, pagination, organization_ids=organization_ids)
    return categories


@router.get(
    "/organizations",
    dependencies=[Depends(RoleChecker([StaticRole.CATEGORIES_MANAGER.name_value]))],
    response_model=PaginationResponse,
)
async def get_organizations_paginated(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
) -> PaginationResponse:
    organization_ids = await RoleChecker.get_user_organization_ids(
        db, current_user, [StaticRole.CATEGORIES_MANAGER.name_value]
    )
    organizations = await OrganizationService.get_paginated_organizations(
        db, pagination, organization_ids=organization_ids
    )

    return organizations


@router.post("")
async def create_category(
    payload: CategoryCreatePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await verify_category_manager_access(db, current_user, str(payload.organization_id))

    is_unique = await CategoryService.is_category_name_unique_in_organization(db, payload.organization_id, payload.name)

    if not is_unique:
        raise HTTPException(status_code=422, detail="Category name must be unique within the organization")

    category = await CategoryService.create_category(db, payload)
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    category = await CategoryService.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await verify_category_manager_access(db, current_user, str(category.organization_id))

    await CategoryService.delete_category(db, category_id=category_id)


@router.put("/{category_id}")
async def update_department(
    category_id: str,
    payload: CategoryUpdatePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    category = await CategoryService.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await verify_category_manager_access(db, current_user, str(category.organization_id))

    if not await CategoryService.validate_unique_name_on_update(db, category_id, payload.name):
        raise HTTPException(status_code=400, detail="Category name must be unique")

    await CategoryService.update_category(db, category_id=category_id, payload=payload)


@router.get("/{category_id}/departments", response_model=PaginationResponse)
async def get_category_departments(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse:
    category = await CategoryService.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await verify_category_manager_access(db, current_user, str(category.organization_id))

    departments = await CategoryService.get_paginated_departments_with_assignment(db, category_id, pagination)
    return departments


@router.post("/{category_id}/synchronize")
async def synchronize_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    category = await CategoryService.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await verify_category_manager_access(db, current_user, str(category.organization_id))

    try:
        await SyncService.sync_category(db, category_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{category_id}/departments/{department_id}/assign")
async def assign_department_to_category(
    category_id: str,
    department_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    category = await CategoryService.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await verify_category_manager_access(db, current_user, str(category.organization_id))

    await CategoryService.assign_department_to_category(db, category_id, department_id)


@router.post("/{category_id}/departments/{department_id}/unassign")
async def unassign_department_from_category(
    category_id: str,
    department_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    category = await CategoryService.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await verify_category_manager_access(db, current_user, str(category.organization_id))

    await CategoryService.unassign_department_from_category(db, category_id, department_id)
