from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional
from passlib.context import CryptContext
from core.config import settings
from fastapi import HTTPException, status
import logging

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