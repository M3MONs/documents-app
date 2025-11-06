import uuid
from pydantic import BaseModel

from schemas.organization import Organization


class Department(BaseModel):
    id: uuid.UUID
    name: str
    organization: Organization

    class Config:
        from_attributes = True