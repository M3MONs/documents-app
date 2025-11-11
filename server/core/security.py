from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from typing import Optional
from passlib.context import CryptContext
from core.config import settings
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from core.database import get_db
from models.user import User
from repositories.user_repository import UserRepository
from schemas.pagination import PaginationParams
from schemas.user import User as UserSchema
from services.organization_service import OrganizationService
from services.user_service import UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, secret_key: str, token_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != token_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")


async def validate_access_token(token: str) -> dict:
    try:
        payload = verify_token(token, settings.JWT_SECRET_KEY)
        if not payload or not payload.get("sub"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
        return payload
    except Exception as e:
        logging.error(f"Access token validation error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")


async def validate_refresh_token(token: str) -> dict:
    try:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
        payload = verify_token(token, settings.JWT_SECRET_KEY, token_type="refresh")
        if not payload or not payload.get("sub"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        return payload
    except Exception as e:
        logging.error(f"Refresh token validation error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = await validate_access_token(token)
    user_id = payload.get("sub")

    user = await UserService.get_user_by_id(db, str(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


class RoleChecker:
    def __init__(self, required_roles: list[str], org_param: str | None = None) -> None:
        self.required_roles = set(required_roles)
        self.org_param = org_param

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        is_superuser = getattr(current_user, "is_superuser", False)

        if is_superuser:
            return

        if not self.org_param:
            validated_user = UserSchema.model_validate(current_user)
            user_roles = set()
            if getattr(validated_user, "roles", None):
                user_roles.update(validated_user.roles)
            if self.required_roles.intersection(user_roles):
                return
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User lacks required roles")

        org_id = None
        if request:
            org_id = request.path_params.get(self.org_param) or request.query_params.get(self.org_param)

        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing organization identifier '{self.org_param}' for role validation",
            )

        has = await UserRepository.user_has_role_in_organization(db, str(current_user.id), self.required_roles, org_id)
        if has:
            return

        if getattr(current_user, "role", None) and current_user.role.name in self.required_roles:
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User lacks required roles {list(self.required_roles)} for organization {org_id}",
        )

    @staticmethod
    async def get_user_organization_ids(db: AsyncSession, current_user: User, required_roles: list[str]) -> list[str]:
        if getattr(current_user, "is_superuser", False):
            all_orgs = await OrganizationService.get_paginated_organizations(
                db,
                PaginationParams(
                    page=1, page_size=100, ordering="name", ordering_desc=False, filter_field=None, filter_value=None
                ),
            )
            return [str(org.id) for org in all_orgs.items]

        user_org_roles = await UserRepository.get_user_organization_roles(db, str(current_user.id))
        accessible_org_ids = set()
        for uor in user_org_roles:
            if uor.role and uor.role.name in required_roles:
                accessible_org_ids.add(str(uor.organization_id))
        return list(accessible_org_ids)
