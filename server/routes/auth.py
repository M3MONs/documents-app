import logging
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from schemas.auth import LoginResponse, LogoutResponse
from models.user import User
from repositories.base_repository import BaseRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from core.security import validate_access_token, validate_refresh_token

security = HTTPBearer()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        token = credentials.credentials
        payload = await validate_access_token(token)
        user_id = payload.get("sub")

        user = await BaseRepository.get_by_id(model=User, db=db, entity_id=str(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return user

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginPayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="The username of the user")
    password: str = Field(..., min_length=8, max_length=100, description="The password of the user")
    provider: str = Field(default="local", description="The authentication provider")

@router.post("/login", response_model=LoginResponse)
async def login(
    login_payload: LoginPayload,
    response: Response = Response(),
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    try:
        user = await AuthService.authenticate(
            provider_name=login_payload.provider,
            db=db,
            username=login_payload.username,
            password=login_payload.password
        )

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        return AuthService.create_login_response(user, response)
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
    payload = await validate_refresh_token(refresh_token)
    user_id = payload.get("sub")
    
    user = await BaseRepository.get_by_id(model=User, db=db, entity_id=str(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return AuthService.create_login_response(user, response)


class RegisterPayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="The desired username")
    email: str | None = Field(None, description="The user's email address")
    password: str = Field(..., min_length=8, max_length=100, description="The desired password")

@router.post("/register", response_model=LoginResponse)
async def register(
    register_payload: RegisterPayload,
    response: Response = Response(),
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    try:
        user = await UserRepository.get_by_username(db, username=register_payload.username)

        if user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

        user = await AuthService.providers["local"].register(
            db,
            username=register_payload.username,
            email=register_payload.email if register_payload.email else "",
            password=register_payload.password
        )

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed")

        return AuthService.create_login_response(user, response)
    except Exception as e:
        logging.error(f"Registration error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))