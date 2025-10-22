from core.providers.local_provider import LocalAuthProvider
from models.user import User


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
