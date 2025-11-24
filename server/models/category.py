from uuid import uuid4
from sqlalchemy import Boolean, Column, UUID, String, ForeignKey, Table, DateTime, func
from sqlalchemy.orm import relationship
from core.database import Base


category_department_visibility = Table(
    "category_department_visibility",
    Base.metadata,
    Column("category_id", UUID, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
    Column("department_id", UUID, ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)

    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization = relationship("Organization", back_populates="categories")
    
    folders = relationship("Folder", back_populates="category", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="category", cascade="all, delete-orphan")
 
    visible_to_departments = relationship(
        "Department", secondary=category_department_visibility, back_populates="visible_categories"
    )