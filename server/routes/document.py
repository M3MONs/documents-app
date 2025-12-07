import uuid
from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import get_current_user
from models.document import VIEWABLE_MIME_TYPES
from schemas.document import DocumentMetadata
from services.document_service import DocumentService


router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> FileResponse:
    document = await DocumentService.get_document_by_id(db, document_id)

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    permitted = await DocumentService.is_user_permitted_to_view_document(db, current_user, document_id)
    if not permitted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this document")

    file_path = await DocumentService.get_file_path(db, document)

    if not DocumentService.is_file_exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on server")

    mime_type = str(document.mime_type) if document.mime_type is not None else "application/octet-stream"
    return FileResponse(path=file_path, filename=str(document.name), media_type=mime_type)


@router.get("/{document_id}/metadata", response_model=DocumentMetadata)
async def get_document_metadata(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> DocumentMetadata:
    document = await DocumentService.get_document_by_id(db, document_id)

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    permitted = await DocumentService.is_user_permitted_to_view_document(db, current_user, document_id)
    if not permitted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this document")

    file_path = await DocumentService.get_file_path(db, document)
    file_exists = DocumentService.is_file_exists(file_path)

    mime_type = str(document.mime_type) if document.mime_type is not None else None
    is_viewable = mime_type in VIEWABLE_MIME_TYPES if mime_type is not None else False

    return DocumentMetadata(
        name=str(document.name),
        mime_type=mime_type,
        file_size=document.file_size,  # pyright: ignore[reportArgumentType]
        created_at=document.created_at,  # pyright: ignore[reportArgumentType]
        updated_at=document.updated_at,  # pyright: ignore[reportArgumentType]
        file_exists=file_exists,
        viewable=is_viewable,
    )


@router.get("/{document_id}/download")
async def download_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> FileResponse:
    document = await DocumentService.get_document_by_id(db, document_id)

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    permitted = await DocumentService.is_user_permitted_to_view_document(db, current_user, document_id)
    if not permitted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this document")

    file_path = await DocumentService.get_file_path(db, document)

    if not DocumentService.is_file_exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on server")

    return FileResponse(
        path=file_path,
        filename=str(document.name),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={document.name}"},
    )
