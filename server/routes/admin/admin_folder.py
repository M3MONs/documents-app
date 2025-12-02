from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

from core.roles import StaticRole
from core.security import get_current_user
from models.user import User
from repositories.user_repository import UserRepository
from schemas.folder import FolderPrivacyUpdate
from schemas.pagination import PaginationParams, PaginationResponse
from services.user_service import UserService
from services.department_service import DepartmentService
from services.folder_service import FolderService
import uuid


router = APIRouter(
    prefix="/admin/folders",
    tags=["admin_folders"],
)


async def verify_folder_manager_access(db: AsyncSession, current_user: User, organization_id: uuid.UUID) -> None:
    if getattr(current_user, "is_superuser", False):
        return

    has_role = await UserRepository.user_has_role_in_organization(db, current_user.id, {StaticRole.CATEGORIES_MANAGER.name_value}, organization_id)  # type: ignore
    if not has_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User lacks required role {StaticRole.CATEGORIES_MANAGER.name_value} for this organization",
        )


@router.get("/{folder_id}/departments")
async def get_departments_assigned_to_folder(
    folder_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse | None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    await verify_folder_manager_access(db, current_user, folder.category.organization_id)  # type: ignore

    return await FolderService.get_paginated_departments_assigned_to_folder(db, pagination, folder_id=folder_id)


@router.post("/{folder_id}/departments/{department_id}/assign")
async def assign_department_to_folder(
    folder_id: uuid.UUID,
    department_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    await verify_folder_manager_access(db, current_user, folder.category.organization_id)  # type: ignore

    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if department.organization_id != folder.category.organization_id:
        raise HTTPException(status_code=400, detail="Department does not belong to the same organization as the folder")

    if await FolderService.is_department_assigned(db, folder_id, department_id):
        raise HTTPException(status_code=400, detail="Department is already assigned to the folder")

    await FolderService.assign_department_to_folder(db, folder, department)


@router.post("/{folder_id}/departments/{department_id}/unassign")
async def unassign_department_from_folder(
    folder_id: uuid.UUID,
    department_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    await verify_folder_manager_access(db, current_user, folder.category.organization_id)  # type: ignore

    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if department.organization_id != folder.category.organization_id:
        raise HTTPException(status_code=400, detail="Department does not belong to the same organization as the folder")

    if not await FolderService.is_department_assigned(db, folder_id, department_id):
        raise HTTPException(status_code=400, detail="Department is not assigned to the folder")

    await FolderService.unassign_department_from_folder(db, folder, department)


@router.get("/{folder_id}/users")
async def get_users_assigned_to_folder(
    folder_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse | None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    await verify_folder_manager_access(db, current_user, folder.category.organization_id)  # type: ignore

    return await FolderService.get_paginated_users_assigned_to_folder(db, pagination, folder_id=folder_id)


@router.post("/{folder_id}/users/{user_id}/assign")
async def assign_user_to_folder(
    folder_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    await verify_folder_manager_access(db, current_user, folder.category.organization_id)  # type: ignore

    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if str(folder.category.organization_id) not in [str(org.id) for org in user.additional_organizations]:
        raise HTTPException(status_code=400, detail="User does not belong to the same organization as the folder")

    if await FolderService.is_user_assigned(db, folder_id, user_id):
        raise HTTPException(status_code=400, detail="User is already assigned to the folder")

    await FolderService.assign_user_to_folder(db, folder, user)


@router.post("/{folder_id}/users/{user_id}/unassign")
async def unassign_user_from_folder(
    folder_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    await verify_folder_manager_access(db, current_user, folder.category.organization_id)  # type: ignore

    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not await FolderService.is_user_assigned(db, folder_id, user_id):
        raise HTTPException(status_code=400, detail="User is not assigned to the folder")

    await FolderService.unassign_user_from_folder(db, folder, user)


@router.patch("/{folder_id}/privacy")
async def set_folder_privacy(
    folder_id: uuid.UUID,
    privacy_update: FolderPrivacyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    await verify_folder_manager_access(db, current_user, folder.category.organization_id)  # type: ignore

    await FolderService.set_folder_private(db, folder_id, privacy_update.is_private)
