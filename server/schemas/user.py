import uuid
from pydantic import BaseModel
from schemas.role import Role
from schemas.organization import Organization

class User(BaseModel):
    id: uuid.UUID
    username: str
    email: str | None = None
    is_active: bool
    is_superuser: bool | None = None
    role: Role | None = None
    primary_organization: Organization | None = None
    additional_organizations: list[Organization] = []
    
    class Config:
        from_attributes = True
        
class UserWithAssignment(User):
    is_assigned: bool | None = None
    is_primary: bool | None = None