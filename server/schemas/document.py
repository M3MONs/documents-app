from pydantic import BaseModel


class DocumentItem(BaseModel):
    id: str
    name: str
    mime_type: str