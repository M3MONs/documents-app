from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.department import Department
from schemas.department import Department as DepartmentSchema
from repositories.base_repository import BaseRepository
from schemas.pagination import PaginationParams, PaginationResponse
from repositories.department_repository import DepartmentRepository
from services.user_service import UserService


class DepartmentService:
    @staticmethod
    async def get_department_by_id(db: AsyncSession, department_id: str) -> Department | None:
        result = await BaseRepository.get_by_id(Department, db, department_id)
        return result

    @staticmethod
    async def get_paginated_departments(
        db: AsyncSession, pagination: PaginationParams, organization_ids: list[str] | None = None
    ) -> PaginationResponse:
        return await BaseRepository.get_paginated(
            model=Department,
            db=db,
            item_schema=DepartmentSchema,
            offset=pagination.offset,
            limit=pagination.page_size,
            ordering=pagination.ordering if pagination.ordering else "name",
            ordering_desc=pagination.ordering_desc,
            filters=pagination.filters,
            options=[selectinload(Department.organization)],
            organization_ids=organization_ids,
        )

    @staticmethod
    async def create_department(db: AsyncSession, payload) -> Department:
        department = Department(**payload.dict())
        await BaseRepository.create(db, department)
        await BaseRepository.refresh(db, department, ["organization"])
        return department

    @staticmethod
    async def delete_department(db: AsyncSession, department_id: str) -> None:
        department = await BaseRepository.get_by_id(Department, db, department_id)
        if department:
            await BaseRepository.delete(model=Department, db=db, entity_id=str(department.id))

    @staticmethod
    async def update_department(db: AsyncSession, department_id: str, payload) -> None:
        department = await BaseRepository.get_by_id(model=Department, db=db, entity_id=department_id)

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(department, field, value)

        await BaseRepository.update(db, department)

    @staticmethod
    async def validate_department_creation(db: AsyncSession, name: str) -> bool:
        return await DepartmentRepository.get_by_name(db, name) is None

    @staticmethod
    async def validate_department_update(db: AsyncSession, department_id: str, new_name: str) -> bool:
        return await DepartmentRepository.validate_unique_name_on_update(db, department_id, new_name)

    @staticmethod
    async def get_paginated_users_with_assignment(
        db: AsyncSession, department_id: str, pagination
    ) -> PaginationResponse:
        return await DepartmentRepository.get_paginated_users_with_assignment(db, department_id, pagination)

    @staticmethod
    async def assign_user_to_department(db: AsyncSession, user_id: str, department_id: str) -> None:
        department = await DepartmentService.get_department_by_id(db, department_id)
        if not department:
            raise ValueError(f"Department with id {department_id} not found")

        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        is_assigned_to_org = str(user.primary_organization_id) == str(department.organization_id) or any(
            str(org.id) == str(department.organization_id) for org in user.additional_organizations
        )
        if not is_assigned_to_org:
            raise ValueError(f"User {user_id} is not assigned to organization {department.organization_id}")

        await DepartmentRepository.assign_user_to_department(db, user_id, department_id)

    @staticmethod
    async def unassign_user_from_department(db: AsyncSession, user_id: str, department_id: str) -> None:
        is_assigned = await DepartmentRepository.is_user_assigned(db, user_id, department_id)

        if not is_assigned:
            raise ValueError(f"User {user_id} is not assigned to department {department_id}")

        await DepartmentRepository.unassign_user_from_department(db, user_id, department_id)

    @staticmethod
    async def is_department_name_unique_by_organization(db: AsyncSession, organization_id: str, name: str) -> bool:
        department = await DepartmentRepository.get_by_name_and_organization(db, name, organization_id)
        return department is None
