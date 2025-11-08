import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from schemas.user import User
from schemas.organization import Organization
from schemas.role import Role


class UserOrganizationRoleCreatePayload(BaseModel):
    user_id: uuid.UUID = Field(..., description="ID of the user to assign the role to")
    organization_id: uuid.UUID = Field(..., description="ID of the organization")
    role_id: uuid.UUID = Field(..., description="ID of the role to assign")
    is_primary: bool = Field(
        False, description="Whether this role is the primary role for the user in the organization"
    )


class UserOrganizationRoleUpdatePayload(BaseModel):
    is_primary: bool = Field(
        False, description="Whether this role is the primary role for the user in the organization"
    )


class UserOrganizationRole(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    role_id: uuid.UUID
    is_primary: bool
    created_at: datetime | None = None

    user: User | None = None
    organization: Organization | None = None
    role: Role | None = None

    class Config:
        from_attributes = True