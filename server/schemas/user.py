from typing import Any
import uuid
from pydantic import BaseModel, Field, field_validator, model_validator
from schemas.organization import Organization


class PasswordResetPayload(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=100, description="The new password for the user")


class UserEditPayload(BaseModel):
    email: str = Field(..., description="The new email for the user")


class Role(BaseModel):
    name: str

    class Config:
        from_attributes = True


class SimpleUserOrganizationRole(BaseModel):
    role: Role | None = None

    class Config:
        from_attributes = True
    
    @property
    def role_name(self) -> str | None:
        return self.role.name if self.role else None



class User(BaseModel):
    id: uuid.UUID
    username: str
    email: str | None = None
    is_active: bool
    is_superuser: bool | None = None
    primary_organization: Organization | None = None
    additional_organizations: list[Organization] = []
    
    roles: list[str] = Field(default_factory=list)
    organization_roles: dict[uuid.UUID, list[str]] = Field(default_factory=dict)
    
    @field_validator('organization_roles', mode='before')
    @classmethod
    def transform_organization_roles(cls, v) -> dict[uuid.UUID, list[str]] | Any:
        if isinstance(v, list):
            result = {}
            for uor in v:
                org_id = getattr(uor, 'organization_id', None)
                role_name = getattr(uor.role, 'name', None) if hasattr(uor, 'role') and uor.role else None
                if org_id and role_name:
                    if org_id not in result:
                        result[org_id] = []
                    result[org_id].append(role_name)
            return result
        return v
    
    @model_validator(mode='after')
    def compute_roles_from_organization_roles(self) -> 'User':    
        if not self.roles and self.organization_roles:
            role_names = set()
            for role_list in self.organization_roles.values():
                role_names.update(role_list)
            self.roles = list(role_names)
        return self


    class Config:
        from_attributes = True
