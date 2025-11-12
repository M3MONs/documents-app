from uuid import uuid4
from sqlalchemy import UUID, Column, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from core.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String(100), unique=True, nullable=False)
    domain = Column(String(255), unique=True, nullable=True) 
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    departments = relationship("Department", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="primary_organization", foreign_keys="User.primary_organization_id")
    user_roles = relationship("UserOrganizationRole", back_populates="organization", cascade="all, delete-orphan", lazy="selectin")
    
    categories = relationship("Category", back_populates="organization", cascade="all, delete-orphan")
