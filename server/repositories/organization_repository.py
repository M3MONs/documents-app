import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from schemas.pagination import PaginationParams, PaginationResponse
from models.user import User, user_organizations


class OrganizationRepository:
    @staticmethod
    async def get_paginated_users_with_assignment(
        db: AsyncSession, organization_id: str, pagination: PaginationParams
    ) -> PaginationResponse:
        from schemas.user import UserWithAssignment
        
        try:
            org_uuid = uuid.UUID(organization_id)
        except ValueError:
            raise ValueError(f"Invalid UUID format for organization_id: {organization_id}")
        
        query = select(User).outerjoin(
            user_organizations,
            (user_organizations.c.user_id == User.id) & (user_organizations.c.organization_id == org_uuid)
        ).add_columns(
            (User.primary_organization_id == org_uuid) | (user_organizations.c.organization_id.isnot(None))
        )

        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar_one()

        if pagination.ordering:
            ordering_column = getattr(User, pagination.ordering, None)
            if ordering_column is not None:
                query = query.order_by(ordering_column.desc() if pagination.ordering_desc else ordering_column.asc())

        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await db.execute(query)
        rows = result.all()

        user_schemas = []
        for row in rows:
            user, is_assigned = row
            user_dict = UserWithAssignment.model_validate(user).dict()
            user_dict['is_assigned'] = is_assigned
            user_dict['is_primary'] = user.primary_organization_id == org_uuid
            user_schemas.append(UserWithAssignment(**user_dict))

        return PaginationResponse(total=total, items=user_schemas)
