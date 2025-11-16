from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.folder import Folder
from repositories.folder_repository import FolderRepository
from repositories.base_repository import BaseRepository


class FolderService:
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
