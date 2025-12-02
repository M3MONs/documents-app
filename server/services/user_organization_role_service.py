from typing import Sequence
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user_organization_role_repository import UserOrganizationRoleRepository
from repositories.base_repository import BaseRepository
from models.user_organization_role import UserOrganizationRole
from schemas.user_organization_role import (
    UserOrganizationRoleCreatePayload,
    UserOrganizationRoleUpdatePayload,
)


class UserOrganizationRoleService:
    @staticmethod
    async def get_by_id(db: AsyncSession, uor_id: uuid.UUID) -> UserOrganizationRole | None:
        return await BaseRepository.get_by_id(model=UserOrganizationRole, db=db, entity_id=uor_id)

    @staticmethod
    async def get_user_organization_roles(db: AsyncSession, user_id: uuid.UUID) -> Sequence[UserOrganizationRole]:
        return await UserOrganizationRoleRepository.get_by_user(db, user_id)

    @staticmethod
    async def assign_role_to_user_in_organization(
        db: AsyncSession, payload: UserOrganizationRoleCreatePayload
    ) -> UserOrganizationRole:
        exists = await UserOrganizationRoleRepository.exists(
            db, payload.user_id, payload.organization_id, payload.role_id
        )

        if exists:
            raise ValueError("User already has this role in the organization")

        return await UserOrganizationRoleRepository.create(db, payload)

    @staticmethod
    async def update_user_organization_role(
        db: AsyncSession, uor_id: uuid.UUID, payload: UserOrganizationRoleUpdatePayload
    ) -> UserOrganizationRole | None:
        return await UserOrganizationRoleRepository.update(db, uor_id, payload)

    @staticmethod
    async def remove_role_from_user_in_organization(db: AsyncSession, uor_id: uuid.UUID) -> bool:
        return await UserOrganizationRoleRepository.delete(db, uor_id)

    @staticmethod
    async def get_user_roles_in_organization(
        db: AsyncSession, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Sequence[UserOrganizationRole]:
        return await UserOrganizationRoleRepository.get_by_user_and_organization(db, user_id, organization_id)
