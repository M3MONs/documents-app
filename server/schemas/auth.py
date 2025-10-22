from typing import Any
from pydantic import BaseModel

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict[str, Any]

class LogoutResponse(BaseModel):
    message: str