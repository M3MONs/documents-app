from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.organization_service import OrganizationService
from models.user import User
from core.database import get_db
from routes.auth import get_current_user


router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/validate/{organization_id}")
async def validate_organization_access(
    organization_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    has_access = await OrganizationService.user_has_access_to_organization(db, str(current_user.id), organization_id)

    if not has_access:
        raise HTTPException(status_code=403, detail="User does not have access to this organization")
