from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.role import Role


class RoleRepository:
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Role | None:
        result = await db.execute(select(Role).where(Role.name == name))
        return result.scalars().first()
    
    @staticmethod
    async def is_user_in_role(db: AsyncSession, user_id: str, role_name: str) -> bool:
        result = await db.execute(
            select(Role)
            .join(Role.users)
            .where(Role.name == role_name)
            .where(Role.users.any(id=user_id))
        )
        role = result.scalars().first()
        return role is not None