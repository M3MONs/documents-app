import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
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
    organization_id: uuid.UUID = Query(..., description="ID of the organization"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[CategorySchema]:
    return await CategoryService.get_categories_for_user_in_organization(db, current_user.id, organization_id) # type: ignore


@router.get("/{category_id}", response_model=CategorySchema)
async def get_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CategorySchema:
    category = await CategoryService.get_category_for_user(db, category_id, current_user.id) # type: ignore
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return CategorySchema.model_validate(category)


@router.get("/{category_id}/content", response_model=CategoryContentResponse)
async def get_category_content_in_folder(
    category_id: uuid.UUID,
    folder_id: uuid.UUID | None = Query(None, description="ID of the folder"),
    search: str | None = Query(None, description="Search query for recursive search in folder/document names"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryContentResponse | None:
    category = await CategoryService.get_category_for_user(db, category_id, current_user.id) # type: ignore
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return await CategoryService.get_category_content_in_folder(
        db, category_id, folder_id, pagination, current_user.id, search_query=search # type: ignore
    )


@router.get("/{category_id}/folder-breadcrumb", response_model=list[dict])
async def get_folder_breadcrumb(
    category_id: uuid.UUID,
    folder_id: uuid.UUID = Query(..., description="ID of the folder"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    category = await CategoryService.get_category_for_user(db, category_id, current_user.id) # type: ignore
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return await CategoryService.get_folder_breadcrumb(db, category, folder_id)