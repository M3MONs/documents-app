from typing import Any, Sequence
import uuid
from sqlalchemy import ColumnElement, Subquery, select, exists, and_, or_, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.category import Category, category_department_visibility
from models.user import user_departments
from models.department import Department
from sqlalchemy.orm import joinedload
from schemas.pagination import PaginationParams, PaginationResponse


class CategoryRepository:
    @staticmethod
    async def get_categories_for_user_in_organization(
        db: AsyncSession, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Sequence[Category]:
        user_departments_subquery = CategoryRepository._get_user_departments_subquery(user_id)
        access_filter = CategoryRepository._get_category_access_filter(user_departments_subquery)

        stmt = (
            select(Category)
            .where(Category.organization_id == organization_id)
            .where(Category.is_active.is_(True))
            .where(access_filter)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_category_for_user(db: AsyncSession, category_id: uuid.UUID, user_id: uuid.UUID) -> Category | None:
        user_departments_subquery = CategoryRepository._get_user_departments_subquery(user_id)
        access_filter = CategoryRepository._get_category_access_filter(user_departments_subquery)

        stmt = (
            select(Category).where(Category.id == category_id).where(Category.is_active.is_(True)).where(access_filter)
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def is_unique_category_name_in_organization(db: AsyncSession, organization_id: uuid.UUID, name: str) -> bool:
        stmt = select(exists().where(and_(Category.organization_id == organization_id, Category.name.ilike(name))))
        result = await db.execute(stmt)
        return not result.scalar()

    @staticmethod
    async def validate_unique_name_on_update(db: AsyncSession, category_id: uuid.UUID, new_name: str) -> bool:
        stmt = select(exists().where(and_(Category.name == new_name, Category.id != category_id)))
        result = await db.execute(stmt)
        return not result.scalar()

    @staticmethod
    async def get_departments_for_category(db: AsyncSession, category_id: uuid.UUID) -> Sequence[Department]:
        stmt = (
            select(Department)
            .join(category_department_visibility)
            .where(category_department_visibility.c.category_id == category_id)
            .options(joinedload(Department.organization))
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def assign_department_to_category(db: AsyncSession, category_id: uuid.UUID, department_id: uuid.UUID) -> None:
        await db.execute(
            insert(category_department_visibility).values(category_id=category_id, department_id=department_id)
        )
        await db.commit()

    @staticmethod
    async def unassign_department_from_category(db: AsyncSession, category_id: uuid.UUID, department_id: uuid.UUID) -> None:
        await db.execute(
            delete(category_department_visibility).where(
                category_department_visibility.c.category_id == category_id,
                category_department_visibility.c.department_id == department_id,
            )
        )
        await db.commit()

    @staticmethod
    async def is_department_assigned_to_category(db: AsyncSession, category_id: uuid.UUID, department_id: uuid.UUID) -> bool:
        stmt = select(
            exists().where(
                category_department_visibility.c.category_id == category_id,
                category_department_visibility.c.department_id == department_id,
            )
        )
        result = await db.execute(stmt)
        return result.scalar() or False

    @staticmethod
    async def get_paginated_departments_with_assignment(
        db: AsyncSession, category_id: uuid.UUID, pagination: PaginationParams
    ) -> PaginationResponse:
        category = await db.get(Category, category_id)
        if not category:
            return PaginationResponse(total=0, items=[])

        query = CategoryRepository._build_departments_query(category.id, category.organization_id) # type: ignore

        total_query = select(Department).where(Department.organization_id == category.organization_id)

        total_result = await db.execute(total_query)
        total = len(total_result.scalars().all())

        if pagination.ordering:
            ordering_column = getattr(Department, pagination.ordering, None)
            if ordering_column is not None:
                query = query.order_by(ordering_column.desc() if pagination.ordering_desc else ordering_column.asc())

        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await db.execute(query)
        rows = result.all()

        items = CategoryRepository._process_rows_to_schemas(rows)

        return PaginationResponse(total=total, items=items)

    @staticmethod
    def _get_user_departments_subquery(user_id: uuid.UUID) -> Subquery:
        return select(user_departments.c.department_id).where(user_departments.c.user_id == user_id).subquery()

    @staticmethod
    def _get_category_access_filter(user_departments_subquery) -> ColumnElement[bool]:
        return or_(
            exists(
                select(1)
                .select_from(category_department_visibility)
                .where(
                    and_(
                        category_department_visibility.c.category_id == Category.id,
                        category_department_visibility.c.department_id.in_(
                            select(user_departments_subquery.c.department_id)
                        ),
                    )
                )
            ),
            Category.is_public.is_(True),
        )
        
    @staticmethod
    def _build_departments_query(category_id: uuid.UUID, organization_id: uuid.UUID):
        return (
            select(Department)
            .where(Department.organization_id == organization_id)
            .add_columns(
                exists(
                    select(1)
                    .select_from(category_department_visibility)
                    .where(
                        category_department_visibility.c.category_id == category_id,
                        category_department_visibility.c.department_id == Department.id,
                    )
                ).label("is_assigned")
            )
        )

    @staticmethod
    def _process_rows_to_schemas(rows) -> list[Any]:
        from schemas.admin import DepartmentWithAssignment

        department_schemas = []
        for row in rows:
            department, is_assigned = row
            department_dict = DepartmentWithAssignment.model_validate(department).dict()
            department_dict["is_assigned"] = is_assigned
            department_schemas.append(DepartmentWithAssignment(**department_dict))
        return department_schemas
