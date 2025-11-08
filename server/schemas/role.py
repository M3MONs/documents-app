import uuid
from pydantic import BaseModel, Field


class RoleCreatePayload(BaseModel):
    name: str = Field(..., description="The name of the new role")
    description: str | None = Field(..., description="The description of the new role")


class Role(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    
    class Config:
        from_attributes = True