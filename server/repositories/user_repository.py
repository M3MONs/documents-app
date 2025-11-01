from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User


class UserRepository:
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: str) -> None:
        await db.execute(update(User).where(User.id == user_id).values(is_active=False))
        await db.commit()
        
    @staticmethod
    async def activate_user(db: AsyncSession, user_id: str) -> None:
        await db.execute(update(User).where(User.id == user_id).values(is_active=True))
        await db.commit()
        