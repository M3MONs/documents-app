import logging
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.config import settings
from schemas.auth import LoginResponse, LogoutResponse
from models.user import User
from repositories.base_repository import BaseRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from core.security import create_access_token, create_refresh_token, verify_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    provider: str = "local",
    username: str = "",
    password: str = "",
    response: Response = Response(),
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    try:
        user = await AuthService.authenticate(provider, db, username=username, password=password)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={"id": user.id, "username": user.username, "email": user.email},
        )
    except ValueError as e:
        logging.error(f"Authentication error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response) -> LogoutResponse:
    try:
        response.delete_cookie(key="refresh_token")
        return LogoutResponse(message="Logged out successfully")
    except Exception as e:
        logging.error(f"Error during logout: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/refresh")
async def refresh_token(
    refresh_token: str = Depends(lambda request: request.cookies.get("refresh_token")),
    db: AsyncSession = Depends(get_db),
    response: Response = Response(),
) -> LoginResponse:
    try:
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

        payload = verify_token(refresh_token, settings.JWT_SECRET_KEY, token_type="refresh")
        user_id = payload.get("sub")

        user = await BaseRepository.get_by_id(model=User, db=db, entity_id=str(user_id))

        if not user_id or not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        access_token = create_access_token(subject=user_id)
        new_refresh_token = create_refresh_token(subject=user_id)

        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={"id": user_id, "username": user.username, "email": user.email},
        )
    except Exception as e:
        logging.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@router.post("/register", response_model=LoginResponse)
async def register(
    username: str,
    email: str,
    password: str,
    response: Response = Response(),
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    try:
        user = await UserRepository.get_by_username(db, username=username)

        if user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

        user = await AuthService.providers["local"].register(db, username=username, email=email, password=password)

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed")

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={"id": user.id, "username": user.username, "email": user.email},
        )
    except Exception as e:
        logging.error(f"Registration error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))