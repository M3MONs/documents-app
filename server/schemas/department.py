import uuid
from pydantic import BaseModel, Field

from schemas.organization import Organization


class DepartmentCreatePayload(BaseModel):
    name: str = Field(..., description="The name for the new department")
    organization_id: uuid.UUID = Field(..., description="The ID of the organization the department belongs to")


class DepartmentUpdatePayload(BaseModel):
    name: str = Field(..., description="The new name for the department")


class Department(BaseModel):
    id: uuid.UUID
    name: str
    organization: Organization

    class Config:
        from_attributes = True
