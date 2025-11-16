from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.document import Document


class DocumentRepository:
    @staticmethod
    async def get_by_file_path(db: AsyncSession, file_path: str) -> Optional[Document]:
        result = await db.execute(select(Document).where(Document.file_path == file_path))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_file_paths(db: AsyncSession, category_id: str) -> set[str]:
        result = await db.execute(select(Document.file_path).where(Document.category_id == category_id))
        return {row[0] for row in result.fetchall()}

    @staticmethod
    async def delete_by_file_path(db: AsyncSession, file_path: str) -> None:
        document = await DocumentRepository.get_by_file_path(db, file_path)
        if document:
            await db.delete(document)
            await db.commit()
