import asyncio
import os
import shutil
from typing import Any, Dict, Optional
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.folder import Folder
from repositories.folder_repository import FolderRepository
from repositories.base_repository import BaseRepository
from schemas.pagination import PaginationResponse
from schemas.folder import FolderUpdate, FolderTreeNode
from core.config import settings
from services.user_service import UserService


class FolderService:
    @staticmethod
    async def get_folder_by_id(db: AsyncSession, folder_id: uuid.UUID) -> Folder | None:
        return await BaseRepository.get_by_id(Folder, db, folder_id)

    @staticmethod
    async def get_folder_by_id_with_category(db: AsyncSession, folder_id: uuid.UUID) -> Optional[Folder]:
        return await FolderRepository.get_by_id_with_category(db, folder_id)

    @staticmethod
    async def get_by_path(db: AsyncSession, category_id: uuid.UUID, path: str) -> Optional[Folder]:
        return await FolderRepository.get_by_path(db, category_id, path)

    @staticmethod
    async def get_all_paths(db: AsyncSession, category_id: uuid.UUID) -> set[str]:
        return await FolderRepository.get_all_paths(db, category_id)

    @staticmethod
    async def create_folder(db: AsyncSession, data: Dict) -> Folder | None:
        folder = Folder(**data)
        await BaseRepository.create(db, folder)
        await BaseRepository.refresh(db, folder, ["category"])
        return folder

    @staticmethod
    async def delete_by_path(db: AsyncSession, category_id: uuid.UUID, path: str) -> None:
        await FolderRepository.delete_by_path(db, category_id, path)

    @staticmethod
    async def is_department_assigned(db: AsyncSession, folder_id: uuid.UUID, department_id: uuid.UUID) -> bool:
        return await FolderRepository.is_department_assigned(db, folder_id, department_id)

    @staticmethod
    async def assign_department_to_folder(db: AsyncSession, folder: Folder, department) -> None:
        await FolderRepository.assign_department_to_folder(db, folder, department)

    @staticmethod
    async def unassign_department_from_folder(db: AsyncSession, folder: Folder, department) -> None:
        await FolderRepository.unassign_department_from_folder(db, folder, department)

    @staticmethod
    async def is_user_assigned(db: AsyncSession, folder_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await FolderRepository.is_user_assigned(db, folder_id, user_id)

    @staticmethod
    async def assign_user_to_folder(db: AsyncSession, folder: Folder, user) -> None:
        await FolderRepository.assign_user_to_folder(db, folder, user)

    @staticmethod
    async def unassign_user_from_folder(db: AsyncSession, folder: Folder, user) -> None:
        await FolderRepository.unassign_user_from_folder(db, folder, user)

    @staticmethod
    async def get_paginated_departments_assigned_to_folder(db: AsyncSession, pagination, folder_id: uuid.UUID) -> PaginationResponse:
        return await FolderRepository.get_paginated_departments_assigned_to_folder(db, folder_id=folder_id, pagination=pagination)

    @staticmethod
    async def get_paginated_users_assigned_to_folder(db: AsyncSession, pagination, folder_id: uuid.UUID) -> PaginationResponse:
        return await FolderRepository.get_paginated_users_assigned_to_folder(db, folder_id=folder_id, pagination=pagination)

    @staticmethod
    async def is_any_department_assigned(db: AsyncSession, folder_id: uuid.UUID, department_ids: list[uuid.UUID]) -> bool:
        return await FolderRepository.is_any_department_assigned(db, folder_id, department_ids)

    @staticmethod
    async def set_folder_private(db: AsyncSession, folder_id: uuid.UUID, is_private: bool) -> None:
        folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")

        sub_folders = await FolderRepository.get_all_child_folders(db, folder_id)

        for sub_folder in sub_folders:
            setattr(sub_folder, "is_private", is_private)
            await BaseRepository.update(db, sub_folder)

        setattr(folder, "is_private", is_private)
        await BaseRepository.update(db, folder)

    @staticmethod
    async def update_folder(db: AsyncSession, folder_id: uuid.UUID, data: FolderUpdate) -> None:
        folder = await FolderService.get_folder_by_id_with_category(db, folder_id)

        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")

        if bool(folder.name != data.name):
            await FolderService._update_folder_name(db, folder, data)

        if bool(folder.is_private != data.is_private) or (data.apply_to_children and not data.is_private):
            await FolderService._update_folder_privacy(db, folder, data)

    @staticmethod
    async def user_has_access_to_folder(db: AsyncSession, folder_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        folder = await FolderService.get_folder_by_id(db, folder_id)

        if not folder:
            return False

        user = await UserService.get_user_by_id(db, user_id)

        if user and bool(user.is_superuser):
            return True

        if not bool(folder.is_private):
            return True

        if await FolderService.is_user_assigned(db, folder_id, user_id):
            return True

        if user:
            department_ids = [department.id for department in user.departments]
            if await FolderService.is_any_department_assigned(db, folder_id, department_ids):
                return True

        return False

    @staticmethod
    async def _update_folder_name(db: AsyncSession, folder: Folder, data: FolderUpdate) -> None:
        existing_folder = await FolderRepository.check_folder_exists_by_name_category_path(db, folder.category_id, data.name, folder.path)  # type: ignore

        if existing_folder:
            raise HTTPException(status_code=400, detail="A folder with this name already exists in the category")

        path_str = str(folder.path)
        new_path = data.name if "." not in path_str else f"{path_str.rsplit('.', 1)[0]}.{data.name}"

        real_old_path = os.path.join(settings.MEDIA_ROOT, "categories", str(folder.category_id), path_str.replace(".", os.sep))
        real_new_path = os.path.join(settings.MEDIA_ROOT, "categories", str(folder.category_id), new_path.replace(".", os.sep))

        await FolderService._rename_folder_in_filesystem(real_old_path, real_new_path)  # type: ignore

        sub_folders = await FolderRepository.get_all_child_folders(db, folder.id)  # type: ignore
        for sub_folder in sub_folders:
            old_sub_path = str(sub_folder.path)
            new_sub_path = old_sub_path.replace(path_str, new_path, 1)
            setattr(sub_folder, "path", new_sub_path)
            await BaseRepository.update(db, sub_folder)

        setattr(folder, "name", data.name)
        setattr(folder, "path", new_path)
        await BaseRepository.update(db, folder)

    @staticmethod
    async def _rename_folder_in_filesystem(old_path: str, new_path: str) -> None:
        try:
            await asyncio.to_thread(os.rename, old_path, new_path)
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"Failed to rename folder in filesystem: {str(e)}")

    @staticmethod
    async def _update_folder_privacy(db: AsyncSession, folder: Folder, data: FolderUpdate) -> None:
        if (data.apply_to_children and not data.is_private) or data.is_private:
            sub_folders = await FolderRepository.get_all_child_folders(db, folder.id)  # type: ignore
            for sub_folder in sub_folders:
                setattr(sub_folder, "is_private", data.is_private)
                await BaseRepository.update(db, sub_folder)

        setattr(folder, "is_private", data.is_private)
        await BaseRepository.update(db, folder)

    @staticmethod
    async def convert_ltree_to_path(ltree_str: Any) -> str:
        return str(ltree_str).replace(".", os.sep)

    @staticmethod
    async def get_category_folder_tree(db: AsyncSession, category_id: uuid.UUID) -> list[FolderTreeNode]:
        root_folders = await FolderRepository.get_folders_by_parent(db, category_id, parent_id=None)
        tree = []
        for folder in root_folders:
            tree.append(await FolderService._build_folder_tree_node(db, folder))
        return tree

    @staticmethod
    async def _validate_folder_exists(db: AsyncSession, folder_id: uuid.UUID) -> Folder:
        folder = await FolderService.get_folder_by_id_with_category(db, folder_id)
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        return folder

    @staticmethod
    async def _get_folders_to_delete(db: AsyncSession, folder_id: uuid.UUID) -> list[Folder]:
        child_folders = list(await FolderRepository.get_all_child_folders(db, folder_id))
        root_folder = await FolderService.get_folder_by_id(db, folder_id)
        if root_folder:
            child_folders.insert(0, root_folder)
        return child_folders

    @staticmethod
    async def _delete_documents_for_folder(db: AsyncSession, folder_to_delete: Folder) -> None:
        from repositories.document_repository import DocumentRepository

        documents = await DocumentRepository.get_documents_by_folder(db, folder_to_delete.category_id, folder_to_delete.id)  # type: ignore

        for doc in documents:
            if doc.folder_id is None:
                file_path = os.path.join(settings.MEDIA_ROOT, "categories", str(doc.category_id), str(doc.name))
            else:
                doc_folder = await FolderService.get_folder_by_id(db, doc.folder_id)  # type: ignore
                if doc_folder:
                    folder_path = str(await FolderService.convert_ltree_to_path(doc_folder.path) if doc_folder.path else doc_folder.name)  # type: ignore
                    file_path = os.path.join(settings.MEDIA_ROOT, "categories", str(doc.category_id), folder_path, str(doc.name))
                else:
                    file_path = os.path.join(settings.MEDIA_ROOT, "categories", str(doc.category_id), str(doc.name))

            await db.delete(doc)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                await db.rollback()
                raise HTTPException(status_code=500, detail="Failed to delete document file, database changes rolled back")

    @staticmethod
    async def _delete_folders_from_db(db: AsyncSession, folders: list[Folder]) -> None:
        for folder_to_delete in reversed(folders):
            await db.delete(folder_to_delete)

    @staticmethod
    async def _delete_folder_from_filesystem(db: AsyncSession, folder: Folder) -> None:
        folder_path = os.path.join(
            settings.MEDIA_ROOT,
            "categories",
            str(folder.category_id),
            str(folder.name) if folder.path is None else await FolderService.convert_ltree_to_path(folder.path),
        )
        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete folder from disk, database changes rolled back")

    @staticmethod
    async def delete_folder(db: AsyncSession, folder_id: uuid.UUID) -> None:
        folder = await FolderService._validate_folder_exists(db, folder_id)

        all_folders_to_delete = await FolderService._get_folders_to_delete(db, folder_id)

        for folder_to_delete in all_folders_to_delete:
            await FolderService._delete_documents_for_folder(db, folder_to_delete)

        await FolderService._delete_folders_from_db(db, all_folders_to_delete)

        await FolderService._delete_folder_from_filesystem(db, folder)

        await db.commit()

    @staticmethod
    async def _build_folder_tree_node(db: AsyncSession, folder: Folder) -> FolderTreeNode:
        children_folders = await FolderRepository.get_folders_by_parent(db, folder.category_id, parent_id=folder.id)  # type: ignore
        children = [await FolderService._build_folder_tree_node(db, child) for child in children_folders]

        return FolderTreeNode(
            id=str(folder.id),  # type: ignore
            name=folder.name,  # type: ignore
            children=children,
        )
