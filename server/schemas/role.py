import uuid
from pydantic import BaseModel


class Role(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    
    class Config:
        from_attributes = True