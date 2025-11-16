from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import Ltree
from sqlalchemy.future import select
from models.folder import Folder


class FolderRepository:
    @staticmethod
    async def get_by_path(db: AsyncSession, category_id: str, path: str) -> Optional[Folder]:
        ltree_path = Ltree(path) if path else None
        result = await db.execute(
            select(Folder).where(
                Folder.category_id == category_id,
                Folder.path == ltree_path
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_paths(db: AsyncSession, category_id: str) -> set[str]:
        result = await db.execute(select(Folder.path).where(Folder.category_id == category_id))
        return {str(row[0]) for row in result.fetchall()}

    @staticmethod
    async def delete_by_path(db: AsyncSession, category_id: str, path: str) -> None:
        folder = await FolderRepository.get_by_path(db, category_id, path)
        if folder:
            await db.delete(folder)
            await db.commit()
