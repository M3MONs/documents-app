import logging
import asyncio
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, Set
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from services.document_service import DocumentService
from services.folder_service import FolderService
from services.category_service import CategoryService


logger = logging.getLogger(__name__)

CATEGORY_MEDIA_ROOT = Path(settings.MEDIA_ROOT) / "categories"


class SyncService:
    @staticmethod
    async def sync_category(db: AsyncSession, category_id: str) -> None:
        category = await CategoryService.get_category_by_id(db, category_id)

        if not category:
            logger.warning(f"Category with ID {category_id} not found.")
            raise ValueError(f"Category with ID {category_id} not found.")

        category_path = CATEGORY_MEDIA_ROOT / str(category.id)

        if not category_path.exists():
            logger.warning(f"Category path {category_path} does not exist.")
            raise FileNotFoundError(f"Category path {category_path} does not exist.")

        scanned_folders, scanned_docs = await SyncService._scan_filesystem(category_path)

        await SyncService._sync_folders(db, category_id, scanned_folders)
        await SyncService._sync_documents(db, category_id, scanned_docs)

        await SyncService._cleanup_orphans(
            db,
            category_id,
            set(scanned_folders.keys()),
            set(scanned_docs.keys()),
        )

        logger.info(f"Synchronized category {category_id}")

    @staticmethod
    async def _scan_filesystem(category_path: Path) -> tuple[Dict[str, dict], Dict[str, dict]]:
        folders = {}
        documents = {}

        for root, dirs, files in category_path.walk():
            # Folders
            for dir_name in dirs:
                dir_path = root / dir_name
                rel_path = dir_path.relative_to(category_path)
                path_str = str(rel_path).replace("\\", ".").replace("/", ".")
                folders[path_str] = {
                    "name": dir_name,
                    "path": path_str,
                    "parent_path": str(rel_path.parent).replace("\\", ".").replace("/", ".") if rel_path.parent != Path(".") else None,
                }

            # Documents
            for file_name in files:
                file_path = root / file_name
                rel_path = file_path.relative_to(category_path)
                file_hash = await asyncio.get_event_loop().run_in_executor(None, SyncService._compute_hash, file_path)
                mime_type, _ = mimetypes.guess_type(str(file_path))
                documents[str(rel_path)] = {
                    "name": file_name,
                    "file_path": str(rel_path),
                    "file_hash": file_hash,
                    "mime_type": mime_type,
                    "file_size": file_path.stat().st_size,
                    "folder_path": str(rel_path.parent) if rel_path.parent != Path(".") else None,
                }

        return folders, documents

    @staticmethod
    def _compute_hash(file_path: Path) -> str:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    @staticmethod
    async def _sync_folders(db: AsyncSession, category_id: str, scanned_folders: Dict[str, dict]) -> None:
        sorted_folders = sorted(scanned_folders.items(), key=lambda x: x[0].count('.'))
        
        for path_str, data in sorted_folders:
            folder = await FolderService.get_by_path(db, category_id, path_str)
            if not folder:
                parent_id = await SyncService._get_parent_folder_id(db, category_id, data["parent_path"])
                
                await FolderService.create_folder(
                    db,
                    {
                        "name": data["name"],
                        "category_id": category_id,
                        "parent_id": parent_id,
                        "path": path_str,
                    },
                )

    @staticmethod
    async def _sync_documents(db: AsyncSession, category_id: str, scanned_docs: Dict[str, dict]) -> None:
        for file_path, data in scanned_docs.items():
            doc = await DocumentService.get_by_file_path(db, file_path)
            if not doc:
                folder_id = await SyncService._get_folder_id_by_path(db, category_id, data["folder_path"])
                
                await DocumentService.create_document(
                    db,
                    {
                        "name": data["name"],
                        "file_path": data["file_path"],
                        "file_hash": data["file_hash"],
                        "mime_type": data["mime_type"],
                        "file_size": data["file_size"],
                        "category_id": category_id,
                        "folder_id": folder_id,
                        "sync_status": "SYNCED",
                    },
                )
            elif doc.file_hash != data["file_hash"]:
                await DocumentService.update_document(
                    db, str(doc.id), {"file_hash": data["file_hash"], "sync_status": "MODIFIED"}
                )

    @staticmethod
    async def _cleanup_orphans(
        db: AsyncSession, category_id: str, scanned_folders: Set[str], scanned_docs: Set[str]
    ) -> None:
        db_folders = await FolderService.get_all_paths(db, category_id)
        to_delete = db_folders - scanned_folders
        for path in to_delete:
            await FolderService.delete_by_path(db, category_id, path)

        db_docs = await DocumentService.get_all_file_paths(db, category_id)
        to_delete = db_docs - scanned_docs
        for path in to_delete:
            await DocumentService.delete_by_file_path(db, path)

    @staticmethod
    async def _get_parent_folder_id(db: AsyncSession, category_id: str, parent_path: str | None) -> str | None:
        if not parent_path:
            return None
        parent = await FolderService.get_by_path(db, category_id, parent_path)
        return str(parent.id) if parent else None

    @staticmethod
    async def _get_folder_id_by_path(db: AsyncSession, category_id: str, folder_path: str | None) -> str | None:
        if not folder_path:
            return None
        folder = await FolderService.get_by_path(db, category_id, folder_path)
        return str(folder.id) if folder else None
