from pydantic import BaseModel, Field, EmailStr, field_validator
from schemas.user import User


class LoginPayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="The username of the user")
    password: str = Field(..., min_length=8, max_length=100, description="The password of the user")
    provider: str = Field(default="local", description="The authentication provider")


class RegisterPayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="The desired username")
    email: EmailStr | None = Field(None, description="The user's email address")
    password: str = Field(..., min_length=8, max_length=100, description="The desired password")

    @field_validator("email", mode='before')
    @classmethod
    def empty_str_to_none(cls, v: str) -> str | None:
        if v == "":
            return None
        return v


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User


class LogoutResponse(BaseModel):
    message: str


class UpdateEmailPayload(BaseModel):
    email: EmailStr


class ChangePasswordPayload(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=100, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
