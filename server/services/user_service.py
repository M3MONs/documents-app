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
    async def get_paginated_users(db: AsyncSession, pagination: PaginationParams, organization_id: str | None = None) -> PaginationResponse:
        if organization_id:
            from repositories.organization_repository import OrganizationRepository
            return await OrganizationRepository.get_paginated_users_with_assignment(db, organization_id, pagination)
        else:
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

    @staticmethod
    async def reset_user_password(db: AsyncSession, user_id: str, new_password: str) -> None:
        from core.security import hash_password

        new_password_hashed = hash_password(new_password)

        user = await BaseRepository.get_by_id(model=User, db=db, entity_id=user_id)

        setattr(user, "hashed_password", new_password_hashed)
        await BaseRepository.update(db, user)


    @staticmethod    
    async def update_user(db: AsyncSession, user_id: str, payload) -> None:
        user = await BaseRepository.get_by_id(model=User, db=db, entity_id=user_id)

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(user, field, value)

        await BaseRepository.update(db, user)
        
    @staticmethod
    async def assign_user_to_organization(db: AsyncSession, user_id: str, organization_id: str, set_primary: bool = False) -> None:
        await UserRepository.assign_user_to_organization(db, user_id, organization_id, set_primary=set_primary)
        
    @staticmethod
    async def unassign_user_from_organization(db: AsyncSession, user_id: str, organization_id: str) -> None:
        await UserRepository.unassign_user_from_organization(db, user_id, organization_id)