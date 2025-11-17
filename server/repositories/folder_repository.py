from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import Ltree
from sqlalchemy.future import select
from models.folder import Folder


class FolderRepository:
    @staticmethod
    async def get_by_path(db: AsyncSession, category_id: str, path: str) -> Optional[Folder]:
        ltree_path = Ltree(path) if path else None
        result = await db.execute(select(Folder).where(Folder.category_id == category_id, Folder.path == ltree_path))
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

    @staticmethod
    async def count_folders_by_parent(db: AsyncSession, category_id: str, parent_id: str | None) -> int:
        from sqlalchemy import func

        query = select(func.count(Folder.id)).where(Folder.category_id == category_id)

        if parent_id:
            query = query.where(Folder.parent_id == parent_id)
        else:
            query = query.where(Folder.parent_id == None)  # noqa: E711

        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def get_folders_by_parent(
        db: AsyncSession, category_id: str, parent_id: str | None, skip: int = 0, limit: int = 20
    ) -> Sequence[Folder]:
        query = select(Folder).where(Folder.category_id == category_id)

        if parent_id:
            query = query.where(Folder.parent_id == parent_id)
        else:
            query = query.where(Folder.parent_id == None)  # noqa: E711

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
