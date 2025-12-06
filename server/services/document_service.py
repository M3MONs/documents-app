import os
import uuid
import hashlib
import mimetypes

from fastapi import HTTPException, UploadFile
from core.config import settings
from repositories.base_repository import BaseRepository
from repositories.document_repository import DocumentRepository
from models.document import Document
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from models.user import User
from services.folder_service import FolderService


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
    async def is_user_permitted_to_view_document(db: AsyncSession, user: User, document_id: uuid.UUID) -> bool:
        return await DocumentRepository.is_user_permitted_to_view_document(db, user, document_id)

    @staticmethod
    async def generate_document_file_path(
        db: AsyncSession, category_id: uuid.UUID, original_filename: str, folder_id: Optional[uuid.UUID] = None
    ) -> str:
        if not folder_id:
            file_path = os.path.join(settings.MEDIA_ROOT, "categories", str(category_id), original_filename)
            return file_path

        folder = await FolderService.get_folder_by_id(db, folder_id)

        if not folder or bool(folder.category_id != category_id):
            raise ValueError("Invalid folder ID for the given category")

        folder_path = await FolderService.convert_ltree_to_path(folder.path)

        return os.path.join(settings.MEDIA_ROOT, "categories", str(category_id), folder_path, original_filename)

    @staticmethod
    async def generate_file_path(db: AsyncSession, document_name: str, folder_id: Optional[uuid.UUID]) -> str:
        if not folder_id:
            return document_name

        folder = await FolderService.get_folder_by_id(db, folder_id)

        if not folder:
            raise ValueError("Invalid folder ID")

        folder_path = await FolderService.convert_ltree_to_path(folder.path)

        return os.path.join(folder_path, document_name)

    @staticmethod
    async def save_document_file(file_path: str, file_data: UploadFile) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file:
            file.write(await file_data.read())

    @staticmethod
    async def get_document_hash(file_path: str) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    async def get_document_mime_type(file_data: UploadFile) -> str:
        mime_type, _ = mimetypes.guess_type(str(file_data.filename))
        return mime_type or "application/octet-stream"

    @staticmethod
    async def generate_document_name(name: str, mime_type: str) -> str:
        extension = mimetypes.guess_extension(mime_type) or ""
        safe_name = "".join(c for c in name if c.isalnum() or c in (" ", ".", "_")).rstrip()
        return f"{safe_name}{extension}"
    
    @staticmethod
    async def cleanup_file(file_path: str) -> None:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to cleanup file {file_path}: {str(e)}")

    @staticmethod
    async def validate_file(file: UploadFile) -> tuple[str, int]:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="File is required")

        mime_type = await DocumentService.get_document_mime_type(file)
        if mime_type not in settings.ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {mime_type}. Allowed types: {', '.join(settings.ALLOWED_MIME_TYPES)}")

        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File size ({file_size} bytes) exceeds maximum allowed size ({settings.MAX_FILE_SIZE} bytes)")

        return mime_type, file_size

    @staticmethod
    async def create_uploaded_document(
        db: AsyncSession,
        name: str,
        mime_type: str,
        file_path: str,
        file_hash: str,
        file_size: int,
        category_id: uuid.UUID,
        folder_id: Optional[uuid.UUID] = None,
    ) -> None:
        await DocumentService.create_document(
            db,
            {
                "name": name,
                "file_path": file_path,
                "file_hash": file_hash,
                "mime_type": mime_type,
                "file_size": file_size,
                "category_id": category_id,
                "folder_id": folder_id,
                "sync_status": "SYNCED",
            },
        )
