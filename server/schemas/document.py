from datetime import datetime
import uuid
from pydantic import BaseModel


class DocumentItem(BaseModel):
    id: str
    name: str
    mime_type: str


class DocumentMetadata(BaseModel):
    name: str
    mime_type: str | None
    file_size: int
    created_at: datetime
    updated_at: datetime
    file_exists: bool
    viewable: bool


class DocumentCreatePayload(BaseModel):
    name: str
    folder_id: uuid.UUID | None = None
    organization_id: uuid.UUID