import uuid
from pydantic import BaseModel

from schemas.organization import Organization

class CategoryCreatePayload(BaseModel):
    name: str
    description: str
    organization_id: str

class Category(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    organization: Organization

    class Config:
        from_attributes = True