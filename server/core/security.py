from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from typing import Optional
from passlib.context import CryptContext
from core.config import settings
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from core.database import get_db
from models.user import User
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        return payload
    except Exception as e:
        logging.error(f"Access token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )

async def validate_refresh_token(token: str) -> dict:
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token missing"
            )
        payload = verify_token(token, settings.JWT_SECRET_KEY, token_type="refresh")
        if not payload or not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        return payload
    except Exception as e:
        logging.error(f"Refresh token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

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

    def __init__(self, required_roles: list[str]) -> None:
        self.required_roles = set(required_roles)

    async def __call__(self, current_user: User = Depends(get_current_user)) -> None:
        is_superuser = getattr(current_user, "is_superuser", False)
        if is_superuser:
            return  

        user_roles = {role.name for role in getattr(current_user, "roles", [])}
        
        if not self.required_roles.intersection(user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User lacks required roles: {list(self.required_roles)}",
            )