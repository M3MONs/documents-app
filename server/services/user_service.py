from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from repositories.user_repository import UserRepository
from repositories.base_repository import BaseRepository

class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user: User) -> User:
        return await BaseRepository.create(db, user)
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
        return await BaseRepository.get_by_id(model=User, db=db, entity_id=user_id)
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        return await UserRepository.get_by_username(db, username=username)
    
    @staticmethod
    async def is_username_taken(db: AsyncSession, username: str) -> bool:
        user = await UserRepository.get_by_username(db, username=username)
        return user is not None
    
    @staticmethod
    async def is_email_taken(db: AsyncSession, email: str) -> bool:
        user = await UserRepository.get_by_email(db, email=email)
        return user is not None