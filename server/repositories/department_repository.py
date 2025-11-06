from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.department import Department


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