from typing import List
import uuid
from pydantic import BaseModel, Field

from schemas.organization import Organization
from schemas.document import DocumentItem
from schemas.folder import FolderItem
from schemas.pagination import PaginationInfo


class CategoryCreatePayload(BaseModel):
    name: str = Field(..., description="The name for the new category")
    description: str = Field(..., description="The description for the new category")
    organization_id: uuid.UUID = Field(..., description="The ID of the organization the category belongs to")
    is_active: bool = Field(..., description="Whether the category is active")
    is_public: bool = Field(..., description="Whether the category is public")


class CategoryUpdatePayload(BaseModel):
    name: str = Field(..., description="The new name for the category")
    description: str = Field(..., description="The new description for the category")
    is_active: bool = Field(..., description="Whether the category is active")
    is_public: bool = Field(..., description="Whether the category is public")


class Category(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    organization: Organization
    is_active: bool
    is_public: bool

    class Config:
        from_attributes = True


class CategoryContentResponse(BaseModel):
    folders: List[FolderItem]
    documents: List[DocumentItem]
    pagination: PaginationInfo

    class Config:
        from_attributes = True
