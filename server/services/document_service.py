from repositories.base_repository import BaseRepository
from repositories.document_repository import DocumentRepository
from models.document import Document
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


class DocumentService:
    @staticmethod
    async def get_document_by_id(db: AsyncSession, document_id: str) -> Optional[Document]:
        return await BaseRepository.get_by_id(Document, db, document_id)

    @staticmethod
    async def get_by_file_path(db: AsyncSession, file_path: str) -> Optional[Document]:
        return await DocumentRepository.get_by_file_path(db, file_path)

    @staticmethod
    async def get_all_file_paths(db: AsyncSession, category_id: str) -> set[str]:
        return await DocumentRepository.get_all_file_paths(db, category_id)

    @staticmethod
    async def create_document(db: AsyncSession, document_data: dict) -> Document | None:
        document = Document(**document_data)
        await BaseRepository.create(db, document)
        await BaseRepository.refresh(db, document, ["category"])
        return document

    @staticmethod
    async def delete_by_file_path(db: AsyncSession, file_path: str) -> None:
        await DocumentRepository.delete_by_file_path(db, file_path)

    @staticmethod
    async def update_document(db: AsyncSession, document_id: str, payload) -> None:
        document = await BaseRepository.get_by_id(model=Document, db=db, entity_id=document_id)

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(document, field, value)

        await BaseRepository.update(db, document)
