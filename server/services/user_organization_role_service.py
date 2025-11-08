from typing import Sequence
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
    async def get_by_id(db: AsyncSession, uor_id: str) -> UserOrganizationRole | None:
        return await BaseRepository.get_by_id(model=UserOrganizationRole, db=db, entity_id=uor_id)

    @staticmethod
    async def get_user_organization_roles(db: AsyncSession, user_id: str) -> Sequence[UserOrganizationRole]:
        return await UserOrganizationRoleRepository.get_by_user(db, user_id)

    @staticmethod
    async def assign_role_to_user_in_organization(
        db: AsyncSession, payload: UserOrganizationRoleCreatePayload
    ) -> UserOrganizationRole:
        exists = await UserOrganizationRoleRepository.exists(
            db, str(payload.user_id), str(payload.organization_id), str(payload.role_id)
        )

        if exists:
            raise ValueError("User already has this role in the organization")

        return await UserOrganizationRoleRepository.create(db, payload)

    @staticmethod
    async def update_user_organization_role(
        db: AsyncSession, uor_id: str, payload: UserOrganizationRoleUpdatePayload
    ) -> UserOrganizationRole | None:
        return await UserOrganizationRoleRepository.update(db, uor_id, payload)

    @staticmethod
    async def remove_role_from_user_in_organization(db: AsyncSession, uor_id: str) -> bool:
        return await UserOrganizationRoleRepository.delete(db, uor_id)

    @staticmethod
    async def get_user_roles_in_organization(
        db: AsyncSession, user_id: str, organization_id: str
    ) -> Sequence[UserOrganizationRole]:
        return await UserOrganizationRoleRepository.get_by_user_and_organization(db, user_id, organization_id)
