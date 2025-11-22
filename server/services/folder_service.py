from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.folder import Folder
from repositories.folder_repository import FolderRepository
from repositories.base_repository import BaseRepository
from schemas.pagination import PaginationResponse


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
    async def get_paginated_departments_assigned_to_folder(
        db: AsyncSession, pagination, folder_id: str
    ) -> PaginationResponse:
        return await FolderRepository.get_paginated_departments_assigned_to_folder(db, folder_id=folder_id, pagination=pagination)