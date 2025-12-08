from typing import Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, select, insert, delete, exists
from models.department import Department
from models.user import User, user_departments
from models.organization import Organization
from schemas.pagination import PaginationParams, PaginationResponse
from schemas.admin import UserWithAssignment


class DepartmentRepository:
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Department | None:
        query = await db.execute(select(Department).where(Department.name == name))
        return query.scalars().first()

    @staticmethod
    async def validate_unique_name_on_update(db: AsyncSession, department_id: uuid.UUID, new_name: str) -> bool:
        query = await db.execute(select(Department).where(Department.name == new_name, Department.id != department_id))
        existing_department = query.scalars().first()
        return existing_department is None

    @staticmethod
    async def assign_user_to_department(db: AsyncSession, user_id: uuid.UUID, department_id: uuid.UUID) -> None:
        await db.execute(insert(user_departments).values(user_id=user_id, department_id=department_id))
        await db.commit()

    @staticmethod
    async def unassign_user_from_department(db: AsyncSession, user_id: uuid.UUID, department_id: uuid.UUID) -> None:
        await db.execute(delete(user_departments).where(user_departments.c.user_id == user_id, user_departments.c.department_id == department_id))
        await db.commit()

    @staticmethod
    async def get_paginated_users_with_assignment(db: AsyncSession, department_id: uuid.UUID, pagination: PaginationParams) -> PaginationResponse:
        department = await db.get(Department, department_id)
        if not department:
            return PaginationResponse(total=0, items=[])

        query = await DepartmentRepository._build_assigned_department_query(department)
        total = await DepartmentRepository._count_total_users_in_organization(db, department.organization_id)  # type: ignore
        query = DepartmentRepository._apply_sorting(query, pagination)
        query = DepartmentRepository._apply_pagination(query, pagination)

        result = await db.execute(query)
        rows = result.all()

        user_schemas = DepartmentRepository._process_rows_to_user_schemas(rows)

        return PaginationResponse(total=total, items=user_schemas)

    @staticmethod
    async def get_by_name_and_organization(db: AsyncSession, name: str, organization_id: uuid.UUID) -> Department | None:
        query = await db.execute(select(Department).where(Department.name == name, Department.organization_id == organization_id))
        return query.scalars().first()

    @staticmethod
    async def is_user_assigned(db: AsyncSession, user_id: uuid.UUID, department_id: uuid.UUID) -> bool | None:
        from sqlalchemy import select, exists
        from models.user import user_departments

        stmt = select(
            exists(
                select(1)
                .select_from(user_departments)
                .where(user_departments.c.user_id == user_id, user_departments.c.department_id == department_id)
            )
        )
        result = await db.execute(stmt)
        is_assigned = result.scalar()
        return is_assigned

    @staticmethod
    async def _build_assigned_department_query(department: Department) -> Select[Any]:
        return (
            select(User)
            .where(
                (User.primary_organization_id == department.organization_id)
                | (User.additional_organizations.any(Organization.id == department.organization_id))
            )
            .add_columns(
                exists(
                    select(1)
                    .select_from(user_departments)
                    .where(user_departments.c.user_id == User.id, user_departments.c.department_id == department.id)
                ).label("is_assigned")
            )
        )

    @staticmethod
    async def _count_total_users_in_organization(db: AsyncSession, organization_id: uuid.UUID) -> int:
        total_query = select(User).where(
            (User.primary_organization_id == organization_id) | (User.additional_organizations.any(Organization.id == organization_id))
        )
        total_result = await db.execute(total_query)
        return len(total_result.scalars().all())

    @staticmethod
    def _apply_sorting(query: Select[Any], pagination: PaginationParams) -> Select[Any]:
        if pagination.ordering:
            ordering_column = getattr(User, pagination.ordering, None)
            if ordering_column is not None:
                query = query.order_by(ordering_column.desc() if pagination.ordering_desc else ordering_column.asc())
        return query

    @staticmethod
    def _apply_pagination(query: Select[Any], pagination: PaginationParams) -> Select[Any]:
        return query.offset(pagination.offset).limit(pagination.page_size)

    @staticmethod
    def _process_rows_to_user_schemas(rows) -> list[UserWithAssignment]:
        user_schemas = []
        for row in rows:
            user, is_assigned = row
            user_dict = UserWithAssignment.model_validate(user).dict()
            user_dict["is_assigned"] = is_assigned
            user_schemas.append(UserWithAssignment(**user_dict))
        return user_schemas
