from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.organization import Organization


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

        organization_to_remove = None
        for org in user.additional_organizations:
            if str(org.id) == organization_id:
                organization_to_remove = org
                break

        if organization_to_remove:
            user.additional_organizations.remove(organization_to_remove)

        if str(user.primary_organization_id) == organization_id:
            setattr(user, "primary_organization_id", None)
            await db.commit()
        else:
            await db.commit()
