from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user_repository import UserRepository
from core.security import verify_password
from models.user import User
from core.auth_base import AuthProvider

class LocalAuthProvider(AuthProvider):
    async def authenticate(self, db: AsyncSession, username: str, password: str) -> User | None:
        user = await UserRepository.get_by_username(db, username)

        if not user:
            return None

        hashed_pass = cast(str, user.hashed_password)
        if not verify_password(password, hashed_pass):
            return None
        
        return user
