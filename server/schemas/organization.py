import uuid
from pydantic import BaseModel, Field


class OrganizationCreatePayload(BaseModel):
    name: str = Field(..., description="The name for the new organization")
    domain: str | None = Field("", description="The domain for the new organization")
    is_active: bool = Field(True, description="Whether the organization is active")


class OrganizationEditPayload(BaseModel):
    name: str = Field(..., description="The new name for the organization")
    domain: str = Field("", description="The new domain for the organization")
    is_active: bool = Field(True, description="Whether the organization is active")


class AssignUserPayload(BaseModel):
    set_primary: bool = Field(False, description="Whether to set the organization as the user's primary organization")


class Organization(BaseModel):
    id: uuid.UUID
    name: str
    domain: str | None = None
    is_active: bool = True

    class Config:
        from_attributes = True