from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import hash_password, verify_password
from models.user import User
from core.auth_base import AuthProvider
from services.user_service import UserService

class LocalAuthProvider(AuthProvider):
    async def authenticate(self, db: AsyncSession, **kwargs) -> User | None:
        username = kwargs.get('username')
        password = kwargs.get('password')
        
        if not username or not password:
            return None
        
        user = await UserService.get_user_by_username(db, username)

        if not user:
            return None

        hashed_pass = cast(str, user.hashed_password)
        if not verify_password(password, hashed_pass):
            return None
        
        return user

    async def register(self, db: AsyncSession, **kwargs) -> User | None:
        username = kwargs.get('username')
        email = kwargs.get('email')
        password = kwargs.get('password')
        
        if not username or not password:
            return None
        
        user = User(username=username, email=email, hashed_password=hash_password(password))
        await UserService.create_user(db, user)
        return user