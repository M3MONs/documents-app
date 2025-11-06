from sqlalchemy.ext.asyncio import AsyncSession
from models.department import Department
from schemas.department import Department as DepartmentSchema
from repositories.base_repository import BaseRepository
from schemas.pagination import PaginationResponse
from repositories.department_repository import DepartmentRepository


class DepartmentService:
    @staticmethod
    async def get_department_by_id(db: AsyncSession, department_id: str) -> Department | None:
        result = await BaseRepository.get_by_id(Department, db, department_id)
        return result
    
    @staticmethod
    async def get_paginated_departments(db: AsyncSession, offset: int, limit: int) -> PaginationResponse:
        return await BaseRepository.get_paginated(
            model=Department,
            db=db,
            item_schema=DepartmentSchema,
            offset=offset,
            limit=limit
        )

    @staticmethod
    async def create_department(db: AsyncSession, payload) -> Department:
        department = Department(**payload.dict())
        await BaseRepository.create(db, department)
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