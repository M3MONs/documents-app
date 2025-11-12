from uuid import uuid4
from sqlalchemy import UUID, Column, String, Boolean, ForeignKey, DateTime, Table, func
from sqlalchemy.orm import relationship
from core.database import Base
from models.folder import folder_user_permissions


user_organizations = Table(
    "user_organizations",
    Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id"), primary_key=True),
    Column("organization_id", UUID, ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
)

user_departments = Table(
    "user_departments",
    Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id"), primary_key=True),
    Column("department_id", UUID, ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    provider = Column(String(50), default="local", nullable=False)
    domain = Column(String(100), nullable=True)

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")

    primary_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    primary_organization = relationship("Organization", back_populates="users", foreign_keys=[primary_organization_id])

    additional_organizations = relationship("Organization", secondary=user_organizations, lazy="selectin")

    departments = relationship("Department", secondary=user_departments, back_populates="users", lazy="selectin")
    organization_roles = relationship("UserOrganizationRole", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    
    accessible_folders = relationship(
        "Folder", secondary=folder_user_permissions, back_populates="allowed_users"
    )
