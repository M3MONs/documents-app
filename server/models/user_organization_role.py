from uuid import uuid4
from sqlalchemy import Column, UUID, ForeignKey, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base

class UserOrganizationRole(Base):
    __tablename__ = "user_organization_roles"
    __table_args__ = (UniqueConstraint("user_id", "organization_id", "role_id", name="uix_user_org_role"),)

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)

    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="organization_roles")
    organization = relationship("Organization", back_populates="user_roles")
    role = relationship("Role")