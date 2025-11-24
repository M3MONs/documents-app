from pydantic import BaseModel


class FolderItem(BaseModel):
    id: str
    name: str
    is_private: bool


class FolderPrivacyUpdate(BaseModel):
    is_private: bool