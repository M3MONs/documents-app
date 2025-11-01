from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from schemas.user import User as UserSchema
from repositories.user_repository import UserRepository
from repositories.base_repository import BaseRepository
from schemas.pagination import PaginationParams, PaginationResponse

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
    
    @staticmethod
    async def get_paginated_users(db: AsyncSession, pagination: PaginationParams) -> PaginationResponse:
        return await BaseRepository.get_paginated(
        model=User,
        db=db,
        item_schema=UserSchema,
        offset=pagination.offset,
        limit=pagination.page_size,
        ordering=pagination.ordering if pagination.ordering else "created_at",
        ordering_desc=pagination.ordering_desc,
        filters=pagination.filters,
    )
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: str) -> None:
        await UserRepository.deactivate_user(db, user_id=user_id)
        
    @staticmethod
    async def activate_user(db: AsyncSession, user_id: str) -> None:
        await UserRepository.activate_user(db, user_id=user_id)