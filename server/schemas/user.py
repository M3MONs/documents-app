import uuid
from pydantic import BaseModel, Field, model_validator
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
    organization_roles: list[SimpleUserOrganizationRole] = Field(default_factory=list)
    
    @model_validator(mode='after')
    def compute_roles_from_organization_roles(self) -> 'User':    
        if not self.roles and self.organization_roles:
            role_names = set()
            for uor in self.organization_roles:
                if uor and hasattr(uor, 'role_name') and uor.role_name:
                    role_names.add(uor.role_name)
            self.roles = list(role_names)
        return self


    class Config:
        from_attributes = True
