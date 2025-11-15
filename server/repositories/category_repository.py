from typing import Sequence
from sqlalchemy import select, exists, and_, or_, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.category import Category, category_department_visibility
from models.user import user_departments
from models.department import Department
from sqlalchemy.orm import joinedload
from schemas.pagination import PaginationParams, PaginationResponse


class CategoryRepository:
    @staticmethod
    async def get_categories_for_user_in_organization(
        db: AsyncSession, user_id: str, organization_id: str
    ) -> Sequence[Category]:
        user_departments_subquery = (
            select(user_departments.c.department_id).where(user_departments.c.user_id == user_id).subquery()
        )

        stmt = (
            select(Category)
            .where(Category.organization_id == organization_id)
            .where(
                or_(
                    ~exists(
                        select(1)
                        .select_from(category_department_visibility)
                        .where(category_department_visibility.c.category_id == Category.id)
                    ),
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
                )
            )
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def is_unique_category_name_in_organization(db: AsyncSession, organization_id: str, name: str) -> bool:
        stmt = select(exists().where(and_(Category.organization_id == organization_id, Category.name.ilike(name))))
        result = await db.execute(stmt)
        return not result.scalar()
    
    @staticmethod
    async def validate_unique_name_on_update(db: AsyncSession, category_id: str, new_name: str) -> bool:
        stmt = select(exists().where(
            and_(
                Category.name == new_name,
                Category.id != category_id
            )
        ))
        result = await db.execute(stmt)
        return not result.scalar()

    @staticmethod
    async def get_departments_for_category(db: AsyncSession, category_id: str) -> Sequence[Department]:
        stmt = (
            select(Department)
            .join(category_department_visibility)
            .where(category_department_visibility.c.category_id == category_id)
            .options(joinedload(Department.organization))
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def assign_department_to_category(db: AsyncSession, category_id: str, department_id: str) -> None:
        await db.execute(
            insert(category_department_visibility).values(
                category_id=category_id, department_id=department_id
            )
        )
        await db.commit()

    @staticmethod
    async def unassign_department_from_category(db: AsyncSession, category_id: str, department_id: str) -> None:
        await db.execute(
            delete(category_department_visibility).where(
                category_department_visibility.c.category_id == category_id,
                category_department_visibility.c.department_id == department_id
            )
        )
        await db.commit()

    @staticmethod
    async def is_department_assigned_to_category(db: AsyncSession, category_id: str, department_id: str) -> bool:
        stmt = select(exists().where(
            category_department_visibility.c.category_id == category_id,
            category_department_visibility.c.department_id == department_id
        ))
        result = await db.execute(stmt)
        return result.scalar() or False

    @staticmethod
    async def get_paginated_departments_with_assignment(
        db: AsyncSession, category_id: str, pagination: PaginationParams
    ) -> PaginationResponse:
        import uuid
        try:
            cat_uuid = uuid.UUID(category_id)
        except ValueError:
            raise ValueError(f"Invalid UUID format for category_id: {category_id}")
        
        category = await db.get(Category, cat_uuid)
        if not category:
            return PaginationResponse(total=0, items=[])

        from schemas.admin import DepartmentWithAssignment
        
        query = select(Department).where(
            Department.organization_id == category.organization_id
        ).add_columns(
            exists(
                select(1).select_from(category_department_visibility).where(
                    category_department_visibility.c.category_id == cat_uuid,
                    category_department_visibility.c.department_id == Department.id
                )
            ).label('is_assigned')
        )

        total_query = select(Department).where(
            Department.organization_id == category.organization_id
        )

        total_result = await db.execute(total_query)
        total = len(total_result.scalars().all())

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
            department_dict['is_assigned'] = is_assigned
            department_schemas.append(DepartmentWithAssignment(**department_dict))

        return PaginationResponse(total=total, items=department_schemas)
