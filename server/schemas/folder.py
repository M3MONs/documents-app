from pydantic import BaseModel
from typing import List


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


class FolderTreeNode(BaseModel):
    id: str
    name: str
    children: List['FolderTreeNode'] = []

FolderTreeNode.model_rebuild()