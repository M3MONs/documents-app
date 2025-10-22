from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User


class AuthProvider(ABC):
    """Abstract base class for authentication providers."""
    
    @abstractmethod
    async def authenticate(self, db: AsyncSession, **kwargs) -> User | None:
        """Authenticate a user and return the User object if successful."""
        pass
        