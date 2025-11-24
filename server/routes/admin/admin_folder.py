from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

from core.roles import StaticRole
from core.security import RoleChecker
from schemas.folder import FolderPrivacyUpdate
from schemas.pagination import PaginationParams, PaginationResponse
from services.user_service import UserService
from services.department_service import DepartmentService
from services.folder_service import FolderService


router = APIRouter(
    prefix="/admin/folders",
    tags=["admin_folders"],
    dependencies=[Depends(RoleChecker([StaticRole.CATEGORIES_MANAGER.name_value]))],
)


@router.get("/{folder_id}/departments")
async def get_departments_assigned_to_folder(
    folder_id: str,
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(),
) -> PaginationResponse | None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    RoleChecker([StaticRole.CATEGORIES_MANAGER.name_value], org_param=str(folder.category.organization_id))

    return await FolderService.get_paginated_departments_assigned_to_folder(db, pagination, folder_id=folder_id)


@router.post("/{folder_id}/departments/{department_id}/assign")
async def assign_department_to_folder(folder_id: str, department_id: str, db: AsyncSession = Depends(get_db)) -> None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if department.organization_id != folder.category.organization_id:
        raise HTTPException(status_code=400, detail="Department does not belong to the same organization as the folder")

    RoleChecker([StaticRole.CATEGORIES_MANAGER.name_value], org_param=str(folder.category.organization_id))

    if await FolderService.is_department_assigned(db, folder_id, department_id):
        raise HTTPException(status_code=400, detail="Department is already assigned to the folder")

    await FolderService.assign_department_to_folder(db, folder, department)


@router.post("/{folder_id}/departments/{department_id}/unassign")
async def unassign_department_from_folder(
    folder_id: str, department_id: str, db: AsyncSession = Depends(get_db)
) -> None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    department = await DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if department.organization_id != folder.category.organization_id:
        raise HTTPException(status_code=400, detail="Department does not belong to the same organization as the folder")

    RoleChecker([StaticRole.CATEGORIES_MANAGER.name_value], org_param=str(folder.category.organization_id))

    if not await FolderService.is_department_assigned(db, folder_id, department_id):
        raise HTTPException(status_code=400, detail="Department is not assigned to the folder")

    await FolderService.unassign_department_from_folder(db, folder, department)


@router.post("/{folder_id}/users/{user_id}/assign")
async def assign_user_to_folder(folder_id: str, user_id: str, db: AsyncSession = Depends(get_db)) -> None:
    folder = await FolderService.get_folder_by_id(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if folder.category.organization_id not in user.additional_organizations:
        raise HTTPException(status_code=400, detail="User does not belong to the same organization as the folder")

    RoleChecker([StaticRole.CATEGORIES_MANAGER.name_value], org_param=str(folder.category.organization_id))

    if await FolderService.is_user_assigned(db, folder_id, user_id):
        raise HTTPException(status_code=400, detail="User is already assigned to the folder")

    await FolderService.assign_user_to_folder(db, folder, user)


@router.post("/{folder_id}/users/{user_id}/unassign")
async def unassign_user_from_folder(folder_id: str, user_id: str, db: AsyncSession = Depends(get_db)) -> None:
    folder = await FolderService.get_folder_by_id(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    RoleChecker([StaticRole.CATEGORIES_MANAGER.name_value], org_param=str(folder.category.organization_id))

    if not await FolderService.is_user_assigned(db, folder_id, user_id):
        raise HTTPException(status_code=400, detail="User is not assigned to the folder")

    await FolderService.unassign_user_from_folder(db, folder, user)


@router.patch("/{folder_id}/privacy")
async def set_folder_privacy(folder_id: str, privacy_update: FolderPrivacyUpdate, db: AsyncSession = Depends(get_db)) -> None:
    folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    RoleChecker([StaticRole.CATEGORIES_MANAGER.name_value], org_param=str(folder.category.organization_id))

    await FolderService.set_folder_private(db, folder_id, privacy_update.is_private)
