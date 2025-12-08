from pathlib import Path
import shutil
from typing import Sequence
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from repositories.category_repository import CategoryRepository
from schemas.category import Category as CategorySchema, CategoryContentResponse, CategoryCreatePayload
from models.category import Category
from models.department import Department
from repositories.base_repository import BaseRepository
from schemas.pagination import PaginationInfo, PaginationParams, PaginationResponse
from core.config import settings
from schemas.document import DocumentItem
from schemas.folder import FolderItem
from services.department_service import DepartmentService

CATEGORY_MEDIA_ROOT = Path(settings.MEDIA_ROOT) / "categories"


class CategoryService:
    @staticmethod
    async def get_categories_for_user_in_organization(db: AsyncSession, user_id: uuid.UUID, organization_id: uuid.UUID) -> Sequence[CategorySchema]:
        categories = await CategoryRepository.get_categories_for_user_in_organization(db, user_id, organization_id)
        return [CategorySchema.model_validate(category) for category in categories]

    @staticmethod
    async def create_category(db: AsyncSession, payload: CategoryCreatePayload) -> CategorySchema:
        category = Category(**payload.model_dump())
        await BaseRepository.create_flush(db, category)

        try:
            CategoryService._create_category_dir(category.id)  # type: ignore
        except FileExistsError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Category directory already exists.")
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")

        await db.commit()
        await BaseRepository.refresh(db, category, ["organization"])
        return CategorySchema.model_validate(category)

    @staticmethod
    async def is_category_name_unique_in_organization(db: AsyncSession, organization_id: uuid.UUID, name: str) -> bool:
        return await CategoryRepository.is_unique_category_name_in_organization(db, organization_id, name)

    @staticmethod
    async def get_paginated_categories(
        db: AsyncSession, pagination: PaginationParams, organization_ids: list[str] | list[uuid.UUID] | None = None
    ) -> PaginationResponse:
        return await BaseRepository.get_paginated(
            model=Category,
            db=db,
            item_schema=CategorySchema,
            offset=pagination.offset,
            limit=pagination.page_size,
            ordering=pagination.ordering if pagination.ordering else "name",
            ordering_desc=pagination.ordering_desc,
            filters=pagination.filters,
            options=[selectinload(Category.organization)],
            organization_ids=organization_ids,
        )

    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: uuid.UUID) -> Category | None:
        return await BaseRepository.get_by_id(Category, db, category_id)

    @staticmethod
    async def get_category_for_user(db: AsyncSession, category_id: uuid.UUID, user_id: uuid.UUID) -> Category | None:
        return await CategoryRepository.get_category_for_user(db, category_id, user_id)

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: uuid.UUID) -> None:
        category = await BaseRepository.get_by_id(Category, db, category_id)

        if category is None:
            raise HTTPException(status_code=404, detail="Category not found.")

        await BaseRepository.delete(Category, db, category_id)

        try:
            CategoryService._delete_category_dir(category.id)  # type: ignore
        except FileNotFoundError:
            pass  # If the directory does not exist, we can ignore this error
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete category directory: {str(e)}")

    @staticmethod
    async def validate_unique_name_on_update(db: AsyncSession, category_id: uuid.UUID, new_name: str) -> bool:
        return await CategoryRepository.validate_unique_name_on_update(db, category_id, new_name)

    @staticmethod
    async def update_category(db: AsyncSession, category_id: uuid.UUID, payload) -> None:
        category = await BaseRepository.get_by_id(model=Category, db=db, entity_id=category_id)

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(category, field, value)

        await BaseRepository.update(db, category)

    @staticmethod
    def _create_category_dir(category_id: uuid.UUID) -> None:
        CATEGORY_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        (CATEGORY_MEDIA_ROOT / str(category_id)).mkdir(exist_ok=False)

    @staticmethod
    def _delete_category_dir(category_id: uuid.UUID) -> None:
        category_path = CATEGORY_MEDIA_ROOT / str(category_id)

        if category_path.exists() and category_path.is_dir():
            shutil.rmtree(category_path)
        else:
            raise FileNotFoundError(f"Category directory {category_path} does not exist.")

    @staticmethod
    async def get_departments_for_category(db: AsyncSession, category_id: uuid.UUID) -> Sequence[Department]:
        return await CategoryRepository.get_departments_for_category(db, category_id)

    @staticmethod
    async def assign_department_to_category(db: AsyncSession, category_id: uuid.UUID, department_id: uuid.UUID) -> None:
        category = await CategoryService.get_category_by_id(db, category_id)
        if not category:
            raise ValueError(f"Category with id {category_id} not found")

        department = await DepartmentService.get_department_by_id(db, department_id)
        if not department:
            raise ValueError(f"Department with id {department_id} not found")

        if str(category.organization_id) != str(department.organization_id):
            raise ValueError("Category and department must belong to the same organization")

        if await CategoryRepository.is_department_assigned_to_category(db, category_id, department_id):
            raise ValueError("Department is already assigned to this category")

        await CategoryRepository.assign_department_to_category(db, category_id, department_id)

    @staticmethod
    async def unassign_department_from_category(db: AsyncSession, category_id: uuid.UUID, department_id: uuid.UUID) -> None:
        is_assigned = await CategoryRepository.is_department_assigned_to_category(db, category_id, department_id)
        if not is_assigned:
            raise ValueError(f"Department {department_id} is not assigned to category {category_id}")

        await CategoryRepository.unassign_department_from_category(db, category_id, department_id)

    @staticmethod
    async def get_paginated_departments_with_assignment(db: AsyncSession, category_id: uuid.UUID, pagination: PaginationParams) -> PaginationResponse:
        return await CategoryRepository.get_paginated_departments_with_assignment(db, category_id, pagination)

    @staticmethod
    async def get_category_content_in_folder(
        db: AsyncSession,
        category_id: uuid.UUID,
        folder_id: uuid.UUID | None,
        pagination: PaginationParams,
        user_id: uuid.UUID,
        search_query: str | None = None,
    ) -> CategoryContentResponse:
        if search_query:
            return await CategoryService._get_category_content_with_search(db, category_id, folder_id, pagination, user_id, search_query)
        else:
            return await CategoryService._get_category_content_without_search(db, category_id, folder_id, pagination, user_id)

    @staticmethod
    async def get_folder_breadcrumb(db: AsyncSession, category, folder_id: uuid.UUID) -> list[dict]:
        from repositories.folder_repository import FolderRepository

        hierarchy = await FolderRepository.get_folder_hierarchy(db, folder_id)

        breadcrumb = [{"id": None, "name": category.name}]
        for folder in hierarchy:
            breadcrumb.append({"id": str(folder.id), "name": str(folder.name)})

        return breadcrumb

    @staticmethod
    async def _get_category_content_with_search(
        db: AsyncSession,
        category_id: uuid.UUID,
        folder_id: uuid.UUID | None,
        pagination: PaginationParams,
        user_id: uuid.UUID,
        search_query: str,
    ) -> CategoryContentResponse:
        from repositories.folder_repository import FolderRepository
        from repositories.document_repository import DocumentRepository
        from services.user_service import UserService

        skip = (pagination.page - 1) * pagination.page_size

        user = await UserService.get_user_by_id(db, user_id)
        is_superuser = bool(user.is_superuser) if user else False
        user_department_ids = [dept.id for dept in user.departments] if user else []

        folders, folder_count = await FolderRepository.search_folders_recursive_with_permissions(
            db=db,
            category_id=category_id,
            user_id=user_id,
            user_department_ids=user_department_ids,
            is_superuser=is_superuser,
            search_query=search_query,
            parent_folder_id=folder_id,
            skip=skip,
            limit=pagination.page_size,
            ordering=pagination.ordering,
            ordering_desc=pagination.ordering_desc,
        )

        folders_returned = len(folders)
        remaining_slots = pagination.page_size - folders_returned

        documents = []
        document_count = 0
        if remaining_slots > 0 or folders_returned == 0:
            doc_skip = max(0, skip - folder_count) if skip >= folder_count else 0
            doc_limit = remaining_slots if folders_returned > 0 else pagination.page_size

            documents, document_count = await DocumentRepository.search_documents_recursive_with_permissions(
                db=db,
                category_id=category_id,
                user_id=user_id,
                user_department_ids=user_department_ids,
                is_superuser=is_superuser,
                search_query=search_query,
                parent_folder_id=folder_id,
                skip=doc_skip,
                limit=doc_limit,
                ordering=pagination.ordering,
                ordering_desc=pagination.ordering_desc,
            )

        total_items = folder_count + document_count
        total_pages = (total_items + pagination.page_size - 1) // pagination.page_size if total_items > 0 else 1

        return CategoryContentResponse(
            folders=[FolderItem(id=str(f.id), name=str(f.name), is_private=bool(f.is_private)) for f in folders],
            documents=[DocumentItem(id=str(d.id), name=str(d.name), mime_type=str(d.mime_type)) for d in documents],
            pagination=PaginationInfo(
                page=pagination.page,
                page_size=pagination.page_size,
                total=total_items,
                total_pages=total_pages,
            ),
        )

    @staticmethod
    async def _get_category_content_without_search(
        db: AsyncSession,
        category_id: uuid.UUID,
        folder_id: uuid.UUID | None,
        pagination: PaginationParams,
        user_id: uuid.UUID,
    ) -> CategoryContentResponse:
        from repositories.folder_repository import FolderRepository
        from repositories.document_repository import DocumentRepository
        from services.folder_service import FolderService

        skip = (pagination.page - 1) * pagination.page_size

        folder_count = await FolderRepository.count_folders_by_parent(
            db, category_id, folder_id, filter_field=pagination.filter_field, filter_value=pagination.filter_value
        )

        folders = await FolderRepository.get_folders_by_parent(
            db,
            category_id,
            folder_id,
            skip=skip,
            limit=pagination.page_size,
            filter_field=pagination.filter_field,
            filter_value=pagination.filter_value,
            ordering=pagination.ordering,
            ordering_desc=pagination.ordering_desc,
        )

        accessible_folders = []
        for folder in folders:
            if await FolderService.user_has_access_to_folder(db, folder.id, user_id):  # type: ignore
                accessible_folders.append(folder)

        folders = accessible_folders
        folders_returned = len(folders)
        remaining_slots = pagination.page_size - folders_returned

        documents = []
        if remaining_slots > 0:
            documents = await DocumentRepository.get_documents_by_folder(
                db,
                category_id,
                folder_id,
                skip=0,
                limit=remaining_slots,
                filter_field=pagination.filter_field,
                filter_value=pagination.filter_value,
                ordering=pagination.ordering,
                ordering_desc=pagination.ordering_desc,
            )

        document_count = await DocumentRepository.count_documents_by_folder(
            db, category_id, folder_id, filter_field=pagination.filter_field, filter_value=pagination.filter_value
        )

        total_items = folder_count + document_count
        total_pages = (total_items + pagination.page_size - 1) // pagination.page_size if total_items > 0 else 1

        return CategoryContentResponse(
            folders=[FolderItem(id=str(f.id), name=str(f.name), is_private=f.is_private) for f in folders],
            documents=[DocumentItem(id=str(d.id), name=str(d.name), mime_type=str(d.mime_type)) for d in documents],
            pagination=PaginationInfo(
                page=pagination.page,
                page_size=pagination.page_size,
                total=total_items,
                total_pages=total_pages,
            ),
        )
