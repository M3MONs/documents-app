from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginationParams, PaginationResponse
from models.organization import Organization
from schemas.organization import Organization as OrganizationSchema
from repositories.base_repository import BaseRepository

class OrganizationService:
    @staticmethod
    async def get_organization_by_id(db: AsyncSession, organization_id: str) -> Organization | None:
        return await BaseRepository.get_by_id(Organization, db, organization_id)
    
    @staticmethod
    async def delete_organization(db: AsyncSession, organization_id: str) -> None:
        organization = await BaseRepository.get_by_id(Organization, db, organization_id)
        if organization:
            await BaseRepository.delete(model=Organization, db=db, entity_id=str(organization.id))
            
    @staticmethod
    async def deactivate_organization(db: AsyncSession, organization_id: str) -> None:
        organization = await BaseRepository.get_by_id(Organization, db, organization_id)
        setattr(organization, "is_active", False)
        await BaseRepository.update(db=db, entity=organization)

    @staticmethod
    async def activate_organization(db: AsyncSession, organization_id: str) -> None:
        organization = await BaseRepository.get_by_id(Organization, db, organization_id)
        setattr(organization, "is_active", True)
        await BaseRepository.update(db=db, entity=organization)

    @staticmethod
    async def get_paginated_organizations(db: AsyncSession, pagination: PaginationParams) -> PaginationResponse:
        return await BaseRepository.get_paginated(
            model=Organization,
            db=db,
            item_schema=OrganizationSchema,
            offset=pagination.offset,
            limit=pagination.page_size,
            ordering=pagination.ordering if pagination.ordering else "created_at",
            ordering_desc=pagination.ordering_desc,
            filters=pagination.filters,
        )
        
    @staticmethod
    async def update_organization(db: AsyncSession, organization_id: str, payload) -> None:
        organization = await BaseRepository.get_by_id(model=Organization, db=db, entity_id=organization_id)

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(organization, field, value)

        await BaseRepository.update(db, organization)
        
    @staticmethod
    async def is_unique_name(db: AsyncSession, name: str) -> bool:
        result = await db.execute(
            select(Organization).where(func.lower(Organization.name) == name.lower())
        )
        organization = result.scalars().first()
        return organization is None
    
    @staticmethod
    async def is_unique_domain(db: AsyncSession, domain: str) -> bool:
        result = await db.execute(
            select(Organization).where(func.lower(Organization.domain) == domain.lower())
        )
        organization = result.scalars().first()
        return organization is None

    @staticmethod
    async def create_organization(db: AsyncSession, payload) -> Organization:
        organization = Organization(**payload.dict())
        await BaseRepository.create(db, organization)
        return organization