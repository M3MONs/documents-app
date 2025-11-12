from uuid import uuid4
from sqlalchemy import UUID, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from models.category import category_department_visibility
from models.folder import folder_department_permissions

class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String(100), nullable=False)

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="departments")

    users = relationship("User", back_populates="department")

    visible_categories = relationship(
        "Category", secondary=category_department_visibility, back_populates="visible_to_departments"
    )
    
    accessible_folders = relationship(
        "Folder", secondary=folder_department_permissions, back_populates="allowed_departments"
    )