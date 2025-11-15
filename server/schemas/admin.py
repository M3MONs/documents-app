import uuid
from pydantic import BaseModel
from schemas.organization import Organization
from schemas.department import Department


class UserAdmin(BaseModel):
    id: uuid.UUID
    username: str
    email: str | None = None
    is_active: bool
    is_superuser: bool | None = None
    primary_organization: Organization | None = None
    additional_organizations: list[Organization] = []


    class Config:
        from_attributes = True


class UserWithAssignment(UserAdmin):
    is_assigned: bool | None = None
    is_primary: bool | None = None


class DepartmentWithAssignment(Department):
    is_assigned: bool | None = None
