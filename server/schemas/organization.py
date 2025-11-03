import uuid
from pydantic import BaseModel


class Organization(BaseModel):
    id: uuid.UUID
    name: str
    domain: str | None = None
    is_active: bool = True

    class Config:
        from_attributes = True