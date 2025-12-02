import os
import uuid
from core.config import settings
from repositories.base_repository import BaseRepository
from repositories.document_repository import DocumentRepository
from models.document import Document
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from models.user import User


class DocumentService:
    @staticmethod
    async def get_document_by_id(db: AsyncSession, document_id: uuid.UUID) -> Optional[Document]:
        return await BaseRepository.get_by_id(Document, db, document_id)

    @staticmethod
    async def get_by_file_path(db: AsyncSession, file_path: str) -> Optional[Document]:
        return await DocumentRepository.get_by_file_path(db, file_path)

    @staticmethod
    async def get_all_file_paths(db: AsyncSession, category_id: uuid.UUID) -> set[str]:
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
    async def update_document(db: AsyncSession, document_id: uuid.UUID, payload) -> None:
        document = await BaseRepository.get_by_id(model=Document, db=db, entity_id=document_id)

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(document, field, value)

        await BaseRepository.update(db, document)

    @staticmethod
    def get_file_path(document: Document) -> str:
        return os.path.join(settings.MEDIA_ROOT, "categories", str(document.category_id), str(document.file_path))

    @staticmethod
    def is_file_exists(file_path: str) -> bool:
        return os.path.isfile(file_path)
    
    @staticmethod
    async def is_user_permitted_to_view_document(
        db: AsyncSession, user: User, document_id: uuid.UUID
    ) -> bool:
        return await DocumentRepository.is_user_permitted_to_view_document(db, user, document_id)
