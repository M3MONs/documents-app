from pydantic import BaseModel
from schemas.user import User


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User


class LogoutResponse(BaseModel):
    message: str
