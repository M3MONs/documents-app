import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from repositories.base_repository import BaseRepository
from models.role import Role
from schemas.role import Role as RoleSchema
from repositories.role_repository import RoleRepository


class RoleService:
    @staticmethod
    async def get_paginated_roles(db: AsyncSession, pagination: PaginationParams) -> PaginationResponse:
        return await BaseRepository.get_paginated(
            model=Role,
            db=db,
            item_schema=RoleSchema,
            offset=pagination.offset,
            limit=pagination.page_size,
            ordering=pagination.ordering if pagination.ordering else "name",
            ordering_desc=pagination.ordering_desc,
            filters=pagination.filters,
        )

    @staticmethod
    async def is_unique_name(db: AsyncSession, name: str) -> bool:
        role = await RoleRepository.get_by_name(db, name)
        return role is None

    @staticmethod
    async def create_role(db: AsyncSession, payload) -> Role:
        role = Role(**payload.dict())
        await BaseRepository.create(db, role)
        return role

    @staticmethod
    async def get_role_by_id(db: AsyncSession, role_id: uuid.UUID) -> Role | None:
        return await BaseRepository.get_by_id(Role, db, role_id)

    @staticmethod
    async def delete_role(db: AsyncSession, role_id: uuid.UUID) -> None:
        role = await BaseRepository.get_by_id(Role, db, role_id)

        if role:
            await BaseRepository.delete(model=Role, db=db, entity_id=str(role.id))
