from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Sequence
from core.database import get_db
from models.user import User
from routes.auth import get_current_user
from schemas.pagination import PaginationParams
from services.category_service import CategoryService
from schemas.category import Category as CategorySchema, CategoryContentResponse


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategorySchema])
async def list_categories(
    organization_id: str = Query(..., description="ID of the organization"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[CategorySchema]:
    return await CategoryService.get_categories_for_user_in_organization(db, str(current_user.id), organization_id)


@router.get("/{category_id}/content", response_model=CategoryContentResponse)
async def get_category_content_in_folder(
    category_id: str,
    folder_id: str | None = Query(None, description="ID of the folder"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryContentResponse | None:
    return await CategoryService.get_category_content_in_folder(db, category_id, folder_id, pagination, str(current_user.id))