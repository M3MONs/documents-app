from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_organization_role import UserOrganizationRole
from schemas.user_organization_role import UserOrganizationRoleCreatePayload, UserOrganizationRoleUpdatePayload


class UserOrganizationRoleRepository:
    @staticmethod
    async def get_by_user_and_organization(db: AsyncSession, user_id: str, organization_id: str) -> Sequence[UserOrganizationRole]:
        stmt = select(UserOrganizationRole).where(
            UserOrganizationRole.user_id == user_id,
            UserOrganizationRole.organization_id == organization_id
        ).options(joinedload(UserOrganizationRole.role), joinedload(UserOrganizationRole.organization))
        res = await db.execute(stmt)
        return res.scalars().all()

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: str) -> Sequence[UserOrganizationRole]:
        stmt = select(UserOrganizationRole).where(
            UserOrganizationRole.user_id == user_id
        ).options(joinedload(UserOrganizationRole.role), joinedload(UserOrganizationRole.organization))
        res = await db.execute(stmt)
        return res.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, payload: UserOrganizationRoleCreatePayload) -> UserOrganizationRole:
        uor = UserOrganizationRole(
            user_id=payload.user_id,
            organization_id=payload.organization_id,
            role_id=payload.role_id,
            is_primary=payload.is_primary
        )
        db.add(uor)
        await db.commit()
        stmt = select(UserOrganizationRole).where(UserOrganizationRole.id == uor.id).options(joinedload(UserOrganizationRole.role), joinedload(UserOrganizationRole.organization))
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def update(db: AsyncSession, uor_id: str, payload: UserOrganizationRoleUpdatePayload) -> UserOrganizationRole | None:
        stmt = update(UserOrganizationRole).where(UserOrganizationRole.id == uor_id).values(**payload.model_dump())
        await db.execute(stmt)
        await db.commit()
        stmt = select(UserOrganizationRole).where(UserOrganizationRole.id == uor_id).options(joinedload(UserOrganizationRole.role), joinedload(UserOrganizationRole.organization))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, uor_id: str) -> bool:
        uor = await db.get(UserOrganizationRole, uor_id)
        if uor:
            await db.delete(uor)
            await db.commit()
            return True
        return False

    @staticmethod
    async def exists(db: AsyncSession, user_id: str, organization_id: str, role_id: str) -> bool:
        stmt = select(UserOrganizationRole).where(
            UserOrganizationRole.user_id == user_id,
            UserOrganizationRole.organization_id == organization_id,
            UserOrganizationRole.role_id == role_id
        ).limit(1)
        res = await db.execute(stmt)
        return res.scalars().first() is not None