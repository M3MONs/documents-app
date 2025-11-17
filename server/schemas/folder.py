from pydantic import BaseModel


class FolderItem(BaseModel):
    id: str
    name: str