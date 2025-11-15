from pathlib import Path
import shutil
from typing import Sequence
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from repositories.category_repository import CategoryRepository
from schemas.category import Category as CategorySchema, CategoryCreatePayload
from models.category import Category
from models.department import Department
from repositories.base_repository import BaseRepository
from schemas.pagination import PaginationParams, PaginationResponse
from core.config import settings
from services.department_service import DepartmentService

CATEGORY_MEDIA_ROOT = Path(settings.MEDIA_ROOT) / "categories"


class CategoryService:
    @staticmethod
    async def get_categories_for_user_in_organization(
        db: AsyncSession, user_id: str, organization_id: str
    ) -> Sequence[CategorySchema]:
        categories = await CategoryRepository.get_categories_for_user_in_organization(db, user_id, organization_id)
        return [CategorySchema.model_validate(category) for category in categories]

    @staticmethod
    async def create_category(db: AsyncSession, payload: CategoryCreatePayload) -> CategorySchema:
        category = Category(**payload.model_dump())
        await BaseRepository.create_flush(db, category)

        try:
            CategoryService._create_category_dir(str(category.id))
        except FileExistsError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Category directory already exists.")
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")

        await db.commit()
        return CategorySchema.model_validate(category)

    @staticmethod
    async def is_category_name_unique_in_organization(db: AsyncSession, organization_id: str, name: str) -> bool:
        return await CategoryRepository.is_unique_category_name_in_organization(db, organization_id, name)

    @staticmethod
    async def get_paginated_categories(
        db: AsyncSession, pagination: PaginationParams, organization_ids: list[str] | None = None
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
    async def get_category_by_id(db: AsyncSession, category_id: str) -> Category | None:
        return await BaseRepository.get_by_id(Category, db, category_id)

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: str) -> None:
        category = await BaseRepository.get_by_id(Category, db, category_id)
        
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found.")

        await BaseRepository.delete(Category, db, category_id)

        try:
            CategoryService._delete_category_dir(str(category.id))
        except FileNotFoundError:
            pass  # If the directory does not exist, we can ignore this error
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete category directory: {str(e)}")

    @staticmethod
    async def validate_unique_name_on_update(db: AsyncSession, category_id: str, new_name: str) -> bool:
        return await CategoryRepository.validate_unique_name_on_update(db, category_id, new_name)

    @staticmethod
    async def update_category(db: AsyncSession, category_id: str, payload) -> None:
        category = await BaseRepository.get_by_id(model=Category, db=db, entity_id=category_id)

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(category, field, value)

        await BaseRepository.update(db, category)

    @staticmethod
    def _create_category_dir(category_id: str) -> None:
        CATEGORY_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        (CATEGORY_MEDIA_ROOT / str(category_id)).mkdir(exist_ok=False)

    @staticmethod
    def _delete_category_dir(category_id: str) -> None:
        category_path = CATEGORY_MEDIA_ROOT / str(category_id)

        if category_path.exists() and category_path.is_dir():
            shutil.rmtree(category_path)
        else:
            raise FileNotFoundError(f"Category directory {category_path} does not exist.")

    @staticmethod
    async def get_departments_for_category(db: AsyncSession, category_id: str) -> Sequence[Department]:
        return await CategoryRepository.get_departments_for_category(db, category_id)

    @staticmethod
    async def assign_department_to_category(db: AsyncSession, category_id: str, department_id: str) -> None:
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
    async def unassign_department_from_category(db: AsyncSession, category_id: str, department_id: str) -> None:
        is_assigned = await CategoryRepository.is_department_assigned_to_category(db, category_id, department_id)
        if not is_assigned:
            raise ValueError(f"Department {department_id} is not assigned to category {category_id}")

        await CategoryRepository.unassign_department_from_category(db, category_id, department_id)

    @staticmethod
    async def get_paginated_departments_with_assignment(
        db: AsyncSession, category_id: str, pagination: PaginationParams
    ) -> PaginationResponse:
        return await CategoryRepository.get_paginated_departments_with_assignment(db, category_id, pagination)
