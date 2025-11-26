from typing import Dict, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.folder import Folder
from repositories.folder_repository import FolderRepository
from repositories.base_repository import BaseRepository
from schemas.pagination import PaginationResponse
from services.user_service import UserService


class FolderService:
    @staticmethod
    async def get_folder_by_id(db: AsyncSession, folder_id: str) -> Folder | None:
        return await BaseRepository.get_by_id(Folder, db, folder_id)

    @staticmethod
    async def get_folder_by_id_with_category(db: AsyncSession, folder_id: str) -> Optional[Folder]:
        return await FolderRepository.get_by_id_with_category(db, folder_id)

    @staticmethod
    async def get_by_path(db: AsyncSession, category_id: str, path: str) -> Optional[Folder]:
        return await FolderRepository.get_by_path(db, category_id, path)

    @staticmethod
    async def get_all_paths(db: AsyncSession, category_id: str) -> set[str]:
        return await FolderRepository.get_all_paths(db, category_id)

    @staticmethod
    async def create_folder(db: AsyncSession, data: Dict) -> Folder | None:
        folder = Folder(**data)
        await BaseRepository.create(db, folder)
        await BaseRepository.refresh(db, folder, ["category"])
        return folder

    @staticmethod
    async def delete_by_path(db: AsyncSession, category_id: str, path: str) -> None:
        await FolderRepository.delete_by_path(db, category_id, path)

    @staticmethod
    async def is_department_assigned(db: AsyncSession, folder_id: str, department_id: str) -> bool:
        return await FolderRepository.is_department_assigned(db, folder_id, department_id)

    @staticmethod
    async def assign_department_to_folder(db: AsyncSession, folder: Folder, department) -> None:
        await FolderRepository.assign_department_to_folder(db, folder, department)

    @staticmethod
    async def unassign_department_from_folder(db: AsyncSession, folder: Folder, department) -> None:
        await FolderRepository.unassign_department_from_folder(db, folder, department)

    @staticmethod
    async def is_user_assigned(db: AsyncSession, folder_id: str, user_id: str) -> bool:
        return await FolderRepository.is_user_assigned(db, folder_id, user_id)

    @staticmethod
    async def assign_user_to_folder(db: AsyncSession, folder: Folder, user) -> None:
        await FolderRepository.assign_user_to_folder(db, folder, user)

    @staticmethod
    async def unassign_user_from_folder(db: AsyncSession, folder: Folder, user) -> None:
        await FolderRepository.unassign_user_from_folder(db, folder, user)

    @staticmethod
    async def get_paginated_departments_assigned_to_folder(db: AsyncSession, pagination, folder_id: str) -> PaginationResponse:
        return await FolderRepository.get_paginated_departments_assigned_to_folder(db, folder_id=folder_id, pagination=pagination)

    @staticmethod
    async def get_paginated_users_assigned_to_folder(db: AsyncSession, pagination, folder_id: str) -> PaginationResponse:
        return await FolderRepository.get_paginated_users_assigned_to_folder(db, folder_id=folder_id, pagination=pagination)

    @staticmethod
    async def is_any_department_assigned(db: AsyncSession, folder_id: str, department_ids: list[str]) -> bool:
        return await FolderRepository.is_any_department_assigned(db, folder_id, department_ids)

    @staticmethod
    async def set_folder_private(db: AsyncSession, folder_id: str, is_private: bool) -> None:
        folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")

        setattr(folder, "is_private", is_private)
        await BaseRepository.update(db, folder)

    @staticmethod
    async def user_has_access_to_folder(db: AsyncSession, folder_id: str, user_id: str) -> bool:
        folder = await FolderService.get_folder_by_id(db, folder_id)

        if not folder:
            return False

        user = await UserService.get_user_by_id(db, user_id)

        if user and bool(user.is_superuser):
            return True

        if not bool(folder.is_private):
            return True

        if await FolderService.is_user_assigned(db, folder_id, user_id):
            return True

        if user:
            department_ids = [str(department.id) for department in user.departments]
            if await FolderService.is_any_department_assigned(db, folder_id, department_ids):
                return True

        return False
