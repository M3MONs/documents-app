from typing import Optional, Sequence
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

    @staticmethod
    async def count_documents_by_folder(
        db: AsyncSession, category_id: str, folder_id: str | None,
        filter_field: Optional[str] = None, filter_value: Optional[str] = None
    ) -> int:
        from sqlalchemy import func

        query = select(func.count(Document.id)).where(Document.category_id == category_id)

        if folder_id:
            query = query.where(Document.folder_id == folder_id)
        else:
            query = query.where(Document.folder_id == None)  # noqa: E711

        if filter_field and filter_value:
            if filter_field == "name":
                query = query.where(Document.name.ilike(f"%{filter_value}%"))
            elif filter_field == "mime_type":
                query = query.where(Document.mime_type.ilike(f"%{filter_value}%"))

        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def get_documents_by_folder(
        db: AsyncSession, category_id: str, folder_id: str | None, skip: int = 0, limit: int = 20,
        filter_field: Optional[str] = None, filter_value: Optional[str] = None,
        ordering: Optional[str] = None, ordering_desc: bool = False
    ) -> Sequence[Document]:
        query = select(Document).where(Document.category_id == category_id)

        if folder_id:
            query = query.where(Document.folder_id == folder_id)
        else:
            query = query.where(Document.folder_id == None)  # noqa: E711

        if filter_field and filter_value:
            if filter_field == "name":
                query = query.where(Document.name.ilike(f"%{filter_value}%"))
            elif filter_field == "mime_type":
                query = query.where(Document.mime_type.ilike(f"%{filter_value}%"))

        if ordering:
            order_column = getattr(Document, ordering, Document.name)
            if ordering_desc:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column)
        else:
            query = query.order_by(Document.name)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
