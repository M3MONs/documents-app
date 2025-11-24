from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.organization import Organization
from models.role import Role
from models.user_organization_role import UserOrganizationRole


class UserRepository:
    @staticmethod
    async def user_has_role_in_organization(
        db: AsyncSession, user_id: str, role_names: set[str] | list[str], organization_id: str
    ) -> bool:
        if not role_names:
            return False

        stmt = (
            select(UserOrganizationRole)
            .join(Role)
            .where(
                UserOrganizationRole.user_id == user_id,
                UserOrganizationRole.organization_id == organization_id,
                Role.name.in_(list(role_names)),
            )
            .limit(1)
        )

        res = await db.execute(stmt)
        row = res.scalars().first()
        return row is not None

    @staticmethod
    async def get_user_organization_roles(db: AsyncSession, user_id: str) -> Sequence[UserOrganizationRole]:
        stmt = (
            select(UserOrganizationRole)
            .where(UserOrganizationRole.user_id == user_id)
            .options(joinedload(UserOrganizationRole.role), joinedload(UserOrganizationRole.organization))
        )
        res = await db.execute(stmt)
        return res.scalars().all()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
        query = (
            select(User)
            .options(
                selectinload(User.organization_roles).selectinload(UserOrganizationRole.role),
                selectinload(User.primary_organization),
                selectinload(User.additional_organizations),
                selectinload(User.departments),
            )
            .where(User.id == user_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.organization_roles).selectinload(UserOrganizationRole.role),
                selectinload(User.primary_organization),
                selectinload(User.additional_organizations),
            )
            .where(User.username == username)
        )
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

    @staticmethod
    async def assign_user_to_organization(
        db: AsyncSession, user_id: str, organization_id: str, set_primary: bool = False
    ) -> None:
        user = await db.get(User, user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} not found")

        if set_primary:
            setattr(user, "primary_organization_id", organization_id)

        if organization_id not in [org.id for org in user.additional_organizations]:
            user.additional_organizations.append(await db.get(Organization, organization_id))

        await db.commit()

    @staticmethod
    async def unassign_user_from_organization(db: AsyncSession, user_id: str, organization_id: str) -> None:
        user = await db.get(User, user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} not found")

        if str(user.primary_organization_id) == organization_id:
            setattr(user, "primary_organization_id", None)
        else:
            organization_to_remove = None
            for org in user.additional_organizations:
                if str(org.id) == organization_id:
                    organization_to_remove = org
                    break
            if organization_to_remove:
                user.additional_organizations.remove(organization_to_remove)

        await db.commit()

    @staticmethod
    async def user_belongs_to_organization(db: AsyncSession, user_id: str, organization_id: str) -> bool:
        user = await db.get(User, user_id)

        if user is None:
            return False

        if str(user.primary_organization_id) == organization_id:
            return True

        for org in user.additional_organizations:
            if str(org.id) == organization_id:
                return True

        return False
