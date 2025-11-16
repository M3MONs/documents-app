import uuid
from pydantic import BaseModel, Field

from schemas.organization import Organization


class CategoryCreatePayload(BaseModel):
    name: str = Field(..., description="The name for the new category")
    description: str = Field(..., description="The description for the new category")
    organization_id: str = Field(..., description="The ID of the organization the category belongs to")


class CategoryUpdatePayload(BaseModel):
    name: str = Field(..., description="The new name for the category")
    description: str = Field(..., description="The new description for the category")


class Category(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    organization: Organization

    class Config:
        from_attributes = True
