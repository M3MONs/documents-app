from sqlalchemy import UUID, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="departments")

    users = relationship("User", back_populates="department")
