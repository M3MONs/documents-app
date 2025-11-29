from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import Ltree
from sqlalchemy.future import select
from sqlalchemy import delete, exists, func
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert as pg_insert
from models.folder import Folder, folder_department_permissions, folder_user_permissions
from models.department import Department
from models.organization import Organization
from schemas.pagination import PaginationParams, PaginationResponse
from schemas.admin import DepartmentWithAssignment
from models.user import User


class FolderRepository:
    @staticmethod
    async def get_by_id_with_category(db: AsyncSession, folder_id: str) -> Optional[Folder]:
        folder_query = select(Folder).options(selectinload(Folder.category)).where(Folder.id == folder_id)
        folder_result = await db.execute(folder_query)
        return folder_result.scalar_one_or_none()

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
    async def count_folders_by_parent(
        db: AsyncSession,
        category_id: str,
        parent_id: str | None,
        filter_field: Optional[str] = None,
        filter_value: Optional[str] = None,
    ) -> int:
        from sqlalchemy import func

        query = select(func.count(Folder.id)).where(Folder.category_id == category_id)

        if parent_id:
            query = query.where(Folder.parent_id == parent_id)
        else:
            query = query.where(Folder.parent_id == None)  # noqa: E711

        if filter_field and filter_value:
            if filter_field == "name":
                query = query.where(Folder.name.ilike(f"%{filter_value}%"))

        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def get_folders_by_parent(
        db: AsyncSession,
        category_id: str,
        parent_id: str | None,
        skip: int = 0,
        limit: int = 20,
        filter_field: Optional[str] = None,
        filter_value: Optional[str] = None,
        ordering: Optional[str] = None,
        ordering_desc: bool = False,
    ) -> Sequence[Folder]:
        query = select(Folder).where(Folder.category_id == category_id)

        if parent_id:
            query = query.where(Folder.parent_id == parent_id)
        else:
            query = query.where(Folder.parent_id == None)  # noqa: E711

        if filter_field and filter_value:
            if filter_field == "name":
                query = query.where(Folder.name.ilike(f"%{filter_value}%"))

        if ordering:
            order_column = getattr(Folder, ordering, Folder.name)
            if ordering_desc:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column)
        else:
            query = query.order_by(Folder.name)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def is_department_assigned(db: AsyncSession, folder_id: str, department_id: str) -> bool:
        result = await db.execute(select(Folder).where(Folder.id == folder_id, Folder.allowed_departments.any(Department.id == department_id)))
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def is_any_department_assigned(db: AsyncSession, folder_id: str, department_ids: list[str]) -> bool:
        result = await db.execute(select(Folder).where(Folder.id == folder_id, Folder.allowed_departments.any(Department.id.in_(department_ids))))
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def assign_department_to_folder(db: AsyncSession, folder: Folder, department: Department) -> None:
        await db.execute(
            pg_insert(folder_department_permissions)
            .values(folder_id=folder.id, department_id=department.id)
            .on_conflict_do_nothing(constraint="folder_department_permissions_pkey")
        )
        child_folders = await FolderRepository.get_all_child_folders(db, str(folder.id))

        if child_folders:
            await db.execute(
                pg_insert(folder_department_permissions)
                .values([{"folder_id": child_folder.id, "department_id": department.id} for child_folder in child_folders])
                .on_conflict_do_nothing(constraint="folder_department_permissions_pkey")
            )

        await db.commit()

    @staticmethod
    async def unassign_department_from_folder(db: AsyncSession, folder: Folder, department: Department) -> None:
        await db.execute(
            delete(folder_department_permissions).where(
                folder_department_permissions.c.folder_id == folder.id,
                folder_department_permissions.c.department_id == department.id,
            )
        )

        child_folders = await FolderRepository.get_all_child_folders(db, str(folder.id))

        if child_folders:
            await db.execute(
                delete(folder_department_permissions).where(
                    folder_department_permissions.c.folder_id.in_([child_folder.id for child_folder in child_folders]),
                    folder_department_permissions.c.department_id == department.id,
                )
            )

        await db.commit()

    @staticmethod
    async def is_user_assigned(db: AsyncSession, folder_id: str, user_id: str) -> bool:
        from models.user import User

        result = await db.execute(select(Folder).where(Folder.id == folder_id, Folder.allowed_users.any(User.id == user_id)))

        return result.scalar_one_or_none() is not None

    @staticmethod
    async def assign_user_to_folder(db: AsyncSession, folder: Folder, user: User) -> None:
        await db.execute(
            pg_insert(folder_user_permissions)
            .values(folder_id=folder.id, user_id=user.id)
            .on_conflict_do_nothing(constraint="folder_user_permissions_pkey")
        )
        child_folders = await FolderRepository.get_all_child_folders(db, str(folder.id))

        if child_folders:
            await db.execute(
                pg_insert(folder_user_permissions)
                .values([{"folder_id": child_folder.id, "user_id": user.id} for child_folder in child_folders])
                .on_conflict_do_nothing(constraint="folder_user_permissions_pkey")
            )

        await db.commit()

    @staticmethod
    async def unassign_user_from_folder(db: AsyncSession, folder: Folder, user: User) -> None:
        await db.execute(
            delete(folder_user_permissions).where(
                folder_user_permissions.c.folder_id == folder.id,
                folder_user_permissions.c.user_id == user.id,
            )
        )

        child_folders = await FolderRepository.get_all_child_folders(db, str(folder.id))

        if child_folders:
            await db.execute(
                delete(folder_user_permissions).where(
                    folder_user_permissions.c.folder_id.in_([child_folder.id for child_folder in child_folders]),
                    folder_user_permissions.c.user_id == user.id,
                )
            )

        await db.commit()

    @staticmethod
    async def get_paginated_departments_assigned_to_folder(db: AsyncSession, folder_id: str, pagination: PaginationParams) -> PaginationResponse:
        folder_query = select(Folder).options(selectinload(Folder.category)).where(Folder.id == folder_id)
        folder_result = await db.execute(folder_query)
        folder = folder_result.scalar_one_or_none()

        if not folder:
            return PaginationResponse(total=0, items=[])

        query = (
            select(Department)
            .where(Department.organization_id == folder.category.organization_id)
            .add_columns(
                exists(
                    select(1)
                    .select_from(folder_department_permissions)
                    .where(
                        folder_department_permissions.c.folder_id == folder_id,
                        folder_department_permissions.c.department_id == Department.id,
                    )
                ).label("is_assigned")
            )
        )

        total_query = select(func.count()).select_from(Department).where(Department.organization_id == folder.category.organization_id)
        total_result = await db.execute(total_query)
        total = total_result.scalar_one()

        if pagination.ordering:
            ordering_column = getattr(Department, pagination.ordering, None)
            if ordering_column is not None:
                query = query.order_by(ordering_column.desc() if pagination.ordering_desc else ordering_column.asc())

        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await db.execute(query)
        rows = result.all()

        department_schemas = []
        for row in rows:
            department, is_assigned = row
            department_dict = DepartmentWithAssignment.model_validate(department).dict()
            department_dict["is_assigned"] = is_assigned
            department_schemas.append(DepartmentWithAssignment(**department_dict))

        return PaginationResponse(total=total, items=department_schemas)

    @staticmethod
    async def get_paginated_users_assigned_to_folder(db: AsyncSession, folder_id: str, pagination: PaginationParams) -> PaginationResponse:
        from models.user import User

        folder_query = select(Folder).options(selectinload(Folder.category)).where(Folder.id == folder_id)
        folder_result = await db.execute(folder_query)
        folder = folder_result.scalar_one_or_none()

        if not folder:
            return PaginationResponse(total=0, items=[])

        query = (
            select(User)
            .where(User.additional_organizations.any(Organization.id == folder.category.organization_id))
            .add_columns(
                exists(
                    select(1)
                    .select_from(folder_user_permissions)  # Zmień na folder_user_permissions
                    .where(
                        folder_user_permissions.c.folder_id == folder_id,  # Zmień na folder_user_permissions.c
                        folder_user_permissions.c.user_id == User.id,  # Zmień na folder_user_permissions.c
                    )
                ).label("is_assigned")
            )
        )

        total_query = (
            select(func.count()).select_from(User).where(User.additional_organizations.any(Organization.id == folder.category.organization_id))
        )
        total_result = await db.execute(total_query)
        total = total_result.scalar_one()

        if pagination.ordering:
            ordering_column = getattr(User, pagination.ordering, None)
            if ordering_column is not None:
                query = query.order_by(ordering_column.desc() if pagination.ordering_desc else ordering_column.asc())

        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await db.execute(query)
        rows = result.all()

        user_schemas = []
        for row in rows:
            user, is_assigned = row
            user_dict = {column.name: getattr(user, column.name) for column in user.__table__.columns}
            user_dict["is_assigned"] = is_assigned
            user_schemas.append(user_dict)

        return PaginationResponse(total=total, items=user_schemas)

    @staticmethod
    async def get_all_child_folders(db: AsyncSession, folder_id: str) -> Sequence[Folder]:
        folder = await FolderRepository.get_by_id_with_category(db, folder_id)

        if not folder:
            return []

        query = select(Folder).where(Folder.category_id == folder.category_id, Folder.path.descendant_of(folder.path))
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_folder_hierarchy(db: AsyncSession, folder_id: str) -> Sequence[Folder]:
        folder = await FolderRepository.get_by_id_with_category(db, folder_id)
        
        if not folder:
            return []
        
        if folder.path is None:
            return [folder]
        
        path_str = str(folder.path)
        path_parts = path_str.split('.')
        
        ancestor_paths = []
        for i in range(len(path_parts)):
            ancestor_path = '.'.join(path_parts[:i+1])
            ancestor_paths.append(Ltree(ancestor_path))
        
        query = select(Folder).where(
            Folder.category_id == folder.category_id,
            Folder.path.in_(ancestor_paths)
        ).order_by(Folder.path)
        
        result = await db.execute(query)
        return result.scalars().all()
