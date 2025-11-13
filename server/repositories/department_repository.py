from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, exists
from models.department import Department
from models.user import User, user_departments
from models.organization import Organization
from schemas.pagination import PaginationParams, PaginationResponse
from schemas.admin import UserWithAssignment


class DepartmentRepository:
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Department | None:
        query = await db.execute(
            select(Department).where(Department.name == name)
        )
        return query.scalars().first()
    
    @staticmethod
    async def validate_unique_name_on_update(db: AsyncSession, department_id: str, new_name: str) -> bool:
        query = await db.execute(
            select(Department).where(
                Department.name == new_name,
                Department.id != department_id
            )
        )
        existing_department = query.scalars().first()
        return existing_department is None

    @staticmethod
    async def assign_user_to_department(db: AsyncSession, user_id: str, department_id: str) -> None:
        await db.execute(
            insert(user_departments).values(user_id=user_id, department_id=department_id)
        )
        await db.commit()

    @staticmethod
    async def unassign_user_from_department(db: AsyncSession, user_id: str, department_id: str) -> None:
        await db.execute(
            delete(user_departments).where(
                user_departments.c.user_id == user_id,
                user_departments.c.department_id == department_id
            )
        )
        await db.commit()

    @staticmethod
    async def get_paginated_users_with_assignment(
        db: AsyncSession, department_id: str, pagination: PaginationParams
    ) -> PaginationResponse:
        import uuid
        try:
            dept_uuid = uuid.UUID(department_id)
        except ValueError:
            raise ValueError(f"Invalid UUID format for department_id: {department_id}")
        
        department = await db.get(Department, dept_uuid)
        if not department:
            return PaginationResponse(total=0, items=[])

        query = select(User).where(
            (User.primary_organization_id == department.organization_id) |
            (User.additional_organizations.any(Organization.id == department.organization_id))
        ).add_columns(
            exists(
                select(1).select_from(user_departments).where(
                    user_departments.c.user_id == User.id,
                    user_departments.c.department_id == dept_uuid
                )
            ).label('is_assigned')
        )

        total_query = select(User).where(
            (User.primary_organization_id == department.organization_id) |
            (User.additional_organizations.any(Organization.id == department.organization_id))
        )

        total_result = await db.execute(total_query)
        total = len(total_result.scalars().all())

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
            user_dict = UserWithAssignment.model_validate(user).dict()
            user_dict['is_assigned'] = is_assigned
            user_schemas.append(UserWithAssignment(**user_dict))

        return PaginationResponse(total=total, items=user_schemas)

    @staticmethod
    async def get_by_name_and_organization(db: AsyncSession, name: str, organization_id: str) -> Department | None:
        query = await db.execute(
            select(Department).where(
                Department.name == name,
                Department.organization_id == organization_id
            )
        )
        return query.scalars().first()
    
    @staticmethod
    async def is_user_assigned(db: AsyncSession, user_id: str, department_id: str) -> bool | None:
        from sqlalchemy import select, exists
        from models.user import user_departments
        stmt = select(exists(
            select(1).select_from(user_departments).where(
                user_departments.c.user_id == user_id,
                user_departments.c.department_id == department_id
            )
        ))
        result = await db.execute(stmt)
        is_assigned = result.scalar()
        return is_assigned