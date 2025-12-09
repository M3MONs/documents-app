from typing import Optional
import uuid
from fastapi import Depends, File, Form, HTTPException, UploadFile, status
from fastapi import APIRouter
from core.roles import StaticRole
from core.security import get_current_user
from core.database import get_db
from models.user import User
from repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.document import UpdateDocumentRequest
from services.document_service import DocumentService
from services.category_service import CategoryService


router = APIRouter(
    prefix="/admin/documents",
    tags=["admin_documents"],
)


async def verify_category_manager_access(db: AsyncSession, current_user: User, organization_id: uuid.UUID) -> None:
    if getattr(current_user, "is_superuser", False):
        return

    has_role = await UserRepository.user_has_role_in_organization(
        db,
        current_user.id,  # type: ignore
        {StaticRole.CATEGORIES_MANAGER.name_value},
        organization_id,  # type: ignore
    )
    if not has_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User lacks required role {StaticRole.CATEGORIES_MANAGER.name_value} for this organization",
        )


@router.post("")
async def create_document(
    name: str = Form(...),
    category_id: str = Form(...),
    folder_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    document_path: Optional[str] = None

    try:
        try:
            category_id_uuid = uuid.UUID(category_id)
            folder_id_uuid = uuid.UUID(folder_id) if folder_id else None
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")

        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="Name is required and cannot be empty")
        name = name.strip()

        mime_type, file_size = await DocumentService.validate_file(file)

        category = await CategoryService.get_category_by_id(db, category_id_uuid)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        await verify_category_manager_access(
            db,
            current_user,
            category.organization_id,  # type: ignore
        )

        document_name = await DocumentService.generate_document_name(name, mime_type)

        existing_document = await DocumentService.get_by_folder_and_name(db, category_id_uuid, folder_id_uuid, document_name)
        if existing_document:
            raise HTTPException(status_code=409, detail=f"Document with name '{document_name}' already exists in this location")

        document_path = await DocumentService.generate_document_file_path(db, category_id_uuid, document_name, folder_id_uuid)

        await DocumentService.save_document_file(document_path, file)

        file_hash = await DocumentService.get_document_hash(document_path)

        try:
            await DocumentService.create_uploaded_document(
                db,
                name=document_name,
                mime_type=mime_type,
                file_hash=file_hash,
                file_size=file_size,
                category_id=category_id_uuid,
                folder_id=folder_id_uuid,
            )
        except Exception as db_error:
            await DocumentService.cleanup_file(document_path)
            raise HTTPException(status_code=500, detail="Failed to save document metadata to database") from db_error

    except HTTPException:
        raise
    except Exception as e:
        if document_path:
            await DocumentService.cleanup_file(document_path)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the document") from e


@router.put("/{document_id}")
async def update_document(
    document_id: str,
    request: UpdateDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        try:
            document_id_uuid = uuid.UUID(document_id)
            name = request.name
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")

        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="Name is required and cannot be empty")
        name = name.strip()

        document = await DocumentService.get_document_by_id(db, document_id_uuid)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        category = await CategoryService.get_category_by_id(db, document.category_id)  # type: ignore
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        await verify_category_manager_access(
            db,
            current_user,
            category.organization_id,  # type: ignore
        )

        await DocumentService.update_document_name(db, document_id_uuid, name)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the document") from e
