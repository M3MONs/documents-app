import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from models.organization import Organization
from schemas.organization import Organization as OrganizationSchema
from repositories.base_repository import BaseRepository


class OrganizationService:
    @staticmethod
    async def get_organization_by_id(db: AsyncSession, organization_id: uuid.UUID) -> Organization | None:
        return await BaseRepository.get_by_id(Organization, db, organization_id)

    @staticmethod
    async def delete_organization(db: AsyncSession, organization_id: uuid.UUID) -> None:
        organization = await BaseRepository.get_by_id(Organization, db, organization_id)
        if organization:
            await BaseRepository.delete(model=Organization, db=db, entity_id=organization.id) # type: ignore

    @staticmethod
    async def get_paginated_organizations(
        db: AsyncSession, pagination: PaginationParams, organization_ids: list[uuid.UUID] | None = None
    ) -> PaginationResponse:
        return await BaseRepository.get_paginated(
            model=Organization,
            db=db,
            item_schema=OrganizationSchema,
            offset=pagination.offset,
            limit=pagination.page_size,
            ordering=pagination.ordering if pagination.ordering else "created_at",
            ordering_desc=pagination.ordering_desc,
            filters=pagination.filters,
            ids=organization_ids,
        )

    @staticmethod
    async def update_organization(db: AsyncSession, organization_id: uuid.UUID, payload) -> None:
        organization = await BaseRepository.get_by_id(model=Organization, db=db, entity_id=organization_id)

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(organization, field, value)

        await BaseRepository.update(db, organization)

    @staticmethod
    async def is_unique_name(db: AsyncSession, name: str) -> bool:
        result = await db.execute(select(Organization).where(func.lower(Organization.name) == name.lower()))
        organization = result.scalars().first()
        return organization is None

    @staticmethod
    async def is_unique_domain(db: AsyncSession, domain: str) -> bool:
        result = await db.execute(select(Organization).where(func.lower(Organization.domain) == domain.lower()))
        organization = result.scalars().first()
        return organization is None

    @staticmethod
    async def create_organization(db: AsyncSession, payload) -> Organization:
        organization = Organization(**payload.dict())
        await BaseRepository.create(db, organization)
        return organization

    @staticmethod
    async def user_has_access_to_organization(db: AsyncSession, user_id: uuid.UUID, organization_id: uuid.UUID) -> bool:
        from repositories.user_repository import UserRepository

        return await UserRepository.user_belongs_to_organization(db, user_id, organization_id)
