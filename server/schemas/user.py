from datetime import datetime
import uuid
from pydantic import BaseModel, Field, field_validator
from schemas.role import Role
from schemas.organization import Organization


class PasswordResetPayload(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=100, description="The new password for the user")


class UserEditPayload(BaseModel):
    email: str = Field(..., description="The new email for the user")


class UserOrganizationRoleUserSchema(BaseModel):
    id: uuid.UUID
    organization_name: str | None = Field(default=None, alias='organization')
    role_name: str | None = Field(default=None, alias='role')
    is_primary: bool
    created_at: datetime | None = None

    @field_validator('organization_name', mode='before')
    @classmethod
    def get_organization_name(cls, v):
        if hasattr(v, 'name'):
            return v.name
        return v

    @field_validator('role_name', mode='before')
    @classmethod
    def get_role_name(cls, v):
        if hasattr(v, 'name'):
            return v.name
        return v

    class Config:
        from_attributes = True


class User(BaseModel):
    id: uuid.UUID
    username: str
    email: str | None = None
    is_active: bool
    is_superuser: bool | None = None
    role: Role | None = None
    organization_roles: list[UserOrganizationRoleUserSchema] = []
    primary_organization: Organization | None = None
    additional_organizations: list[Organization] = []

    class Config:
        from_attributes = True


class UserWithAssignment(User):
    is_assigned: bool | None = None
    is_primary: bool | None = None
