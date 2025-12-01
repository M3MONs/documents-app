from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.document import Document
from models.user import User


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
    async def get_by_id_with_category(db: AsyncSession, document_id: str) -> Optional[Document]:
        result = await db.execute(
            select(Document).where(Document.id == document_id).options(selectinload(Document.category))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_by_file_path(db: AsyncSession, file_path: str) -> None:
        document = await DocumentRepository.get_by_file_path(db, file_path)
        if document:
            await db.delete(document)
            await db.commit()

    @staticmethod
    async def count_documents_by_folder(
        db: AsyncSession,
        category_id: str,
        folder_id: str | None,
        filter_field: Optional[str] = None,
        filter_value: Optional[str] = None,
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
        db: AsyncSession,
        category_id: str,
        folder_id: str | None,
        skip: int = 0,
        limit: int = 20,
        filter_field: Optional[str] = None,
        filter_value: Optional[str] = None,
        ordering: Optional[str] = None,
        ordering_desc: bool = False,
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

    @staticmethod
    async def is_user_permitted_to_view_document(db: AsyncSession, user: User, document_id: str) -> bool:
        from repositories.folder_repository import FolderRepository

        document = await DocumentRepository.get_by_id_with_category(db, document_id)
        if not document:
            return False

        user_org_ids = [str(org.id) for org in user.additional_organizations]
        if str(document.category.organization_id) not in user_org_ids:
            return False

        if document.folder_id is not None:
            folder = await FolderRepository.get_by_id_with_category(db, str(document.folder_id))

            if folder and bool(folder.is_private):
                from services.folder_service import FolderService

                has_access = await FolderService.user_has_access_to_folder(db, str(folder.id), str(user.id))
                if not has_access:
                    return False

        return True

    @staticmethod
    async def search_documents_recursive_with_permissions(
        db: AsyncSession,
        category_id: str,
        user_id: str,
        user_department_ids: list[str],
        is_superuser: bool,
        search_query: str,
        parent_folder_id: str | None = None,
        skip: int = 0,
        limit: int = 20,
        ordering: Optional[str] = None,
        ordering_desc: bool = False,
    ) -> tuple[Sequence[Document], int]:
        from sqlalchemy import or_, and_, literal, func
        from models.folder import Folder, folder_user_permissions, folder_department_permissions
        from repositories.folder_repository import FolderRepository

        base_conditions = [Document.category_id == category_id]

        if search_query:
            base_conditions.append(Document.name.ilike(f"%{search_query}%"))

        if parent_folder_id:
            parent_folder = await FolderRepository.get_by_id_with_category(db, parent_folder_id)
            if parent_folder and parent_folder.path is not None:
                subtree_folder_ids_query = select(Folder.id).where(
                    Folder.category_id == category_id, Folder.path.descendant_of(parent_folder.path)
                )
                base_conditions.append(
                    or_(Document.folder_id.in_(subtree_folder_ids_query), Document.folder_id == parent_folder_id)
                )

        if not is_superuser:
            folder_not_private = (
                select(literal(1))
                .select_from(Folder)
                .where(
                    Folder.id == Document.folder_id,
                    Folder.is_private == False,  # noqa: E712
                )
                .exists()
            )

            user_assigned_to_folder = (
                select(literal(1))
                .select_from(folder_user_permissions)
                .where(
                    folder_user_permissions.c.folder_id == Document.folder_id,
                    folder_user_permissions.c.user_id == user_id,
                )
                .exists()
            )

            permission_conditions = [
                Document.folder_id == None,  # noqa: E711
                folder_not_private,
                user_assigned_to_folder,
            ]

            if user_department_ids:
                dept_assigned_to_folder = (
                    select(literal(1))
                    .select_from(folder_department_permissions)
                    .where(
                        folder_department_permissions.c.folder_id == Document.folder_id,
                        folder_department_permissions.c.department_id.in_(user_department_ids),
                    )
                    .exists()
                )
                permission_conditions.append(dept_assigned_to_folder)

            base_conditions.append(or_(*permission_conditions))

        count_query = select(func.count(Document.id)).where(and_(*base_conditions))
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        query = select(Document).where(and_(*base_conditions))

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

        return result.scalars().all(), total
