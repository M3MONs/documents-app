from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from repositories.category_repository import CategoryRepository
from schemas.category import Category as CategorySchema, CategoryCreatePayload
from models.category import Category
from repositories.base_repository import BaseRepository
from schemas.pagination import PaginationParams, PaginationResponse


class CategoryService:
    @staticmethod
    async def get_categories_for_user_in_organization(
        db: AsyncSession, user_id: str, organization_id: str
    ) -> Sequence[CategorySchema]:
        categories = await CategoryRepository.get_categories_for_user_in_organization(db, user_id, organization_id)
        return [CategorySchema.model_validate(category) for category in categories]

    @staticmethod
    async def create_category(db: AsyncSession, payload: CategoryCreatePayload) -> CategorySchema:
        category = Category(**payload.dict())
        await BaseRepository.create(db, category)
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
        if category:
            await BaseRepository.delete(model=Category, db=db, entity_id=str(category.id))

    @staticmethod
    async def validate_unique_name_on_update(db: AsyncSession, category_id: str, new_name: str) -> bool:
        return await CategoryRepository.validate_unique_name_on_update(db, category_id, new_name)

    @staticmethod
    async def update_category(db: AsyncSession, category_id: str, payload) -> None:
        category = await BaseRepository.get_by_id(model=Category, db=db, entity_id=category_id)

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(category, field, value)

        await BaseRepository.update(db, category)
