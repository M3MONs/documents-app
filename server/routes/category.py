
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Sequence
from core.database import get_db
from models.user import User
from routes.auth import get_current_user
from services.category_service import CategoryService
from schemas.category import Category as CategorySchema


router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategorySchema])
async def list_categories(
    organization_id: str = Query(..., description="ID of the organization"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Sequence[CategorySchema]:
    return await CategoryService.get_categories_for_user_in_organization(
        db, str(current_user.id), organization_id
    )