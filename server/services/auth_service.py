from fastapi import Response
from core.providers.local_provider import LocalAuthProvider
from models.user import User
from schemas.auth import LoginResponse
from core.security import create_access_token, create_refresh_token
from core.config import settings


class AuthService:
    providers = {
        "local": LocalAuthProvider(),
    }

    @staticmethod
    async def authenticate(provider_name: str, db, **credentials) -> User | None:
        provider = AuthService.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Unknown auth provider: {provider_name}")
        return await provider.authenticate(db, **credentials)
    
    @staticmethod
    def create_login_response(user: User, response: Response) -> LoginResponse:
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