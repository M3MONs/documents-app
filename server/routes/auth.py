from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from schemas.auth import LoginResponse, LogoutResponse
from models.user import User
from services.user_service import UserService
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

    user = await UserService.get_user_by_id(db, str(user_id))
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
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    user = await AuthService.authenticate(
        provider_name=login_payload.provider, db=db, username=login_payload.username, password=login_payload.password
    )

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return AuthService.create_login_response(user, response)


@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response) -> LogoutResponse:
    response.delete_cookie(key="refresh_token")
    return LogoutResponse(message="Logged out successfully")


@router.get("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str = Depends(lambda request: request.cookies.get("refresh_token")),
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    payload = await validate_refresh_token(refresh_token)
    user_id = payload.get("sub")

    user = await UserService.get_user_by_id(db, str(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return AuthService.create_login_response(user, response)


class RegisterPayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="The desired username")
    email: EmailStr | None = Field(None, description="The user's email address")
    password: str = Field(..., min_length=8, max_length=100, description="The desired password")


@router.post("/register", response_model=LoginResponse)
async def register(
    register_payload: RegisterPayload,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    if await UserService.is_username_taken(db, register_payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    if register_payload.email and await UserService.is_email_taken(db, register_payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

    user = await AuthService.providers["local"].register(
        db,
        username=register_payload.username,
        email=register_payload.email,
        password=register_payload.password,
    )

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed")

    return AuthService.create_login_response(user, response)
