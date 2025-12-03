from pydantic import BaseModel


class FolderItem(BaseModel):
    id: str
    name: str
    is_private: bool


class FolderPrivacyUpdate(BaseModel):
    is_private: bool


class FolderUpdate(BaseModel):
    name: str
    is_private: bool
    apply_to_children: bool