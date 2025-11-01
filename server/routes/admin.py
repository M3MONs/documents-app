from fastapi import APIRouter, Depends
from core.security import RoleChecker
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.user import User
from schemas.user import User as UserSchema
from repositories.base_repository import BaseRepository
from schemas.pagination import PaginationParams, PaginationResponse


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", dependencies=[Depends(RoleChecker(["admin"]))], response_model=PaginationResponse)
async def get_users_paginated(
    db: AsyncSession = Depends(get_db), pagination: PaginationParams = Depends()
) -> PaginationResponse:
    users = await BaseRepository.get_paginated(
        model=User,
        db=db,
        item_schema=UserSchema,
        offset=pagination.offset,
        limit=pagination.page_size,
        ordering=pagination.ordering if pagination.ordering else "created_at",
        ordering_desc=pagination.ordering_desc,
        filters=pagination.filters,
    )

    return users
