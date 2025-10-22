from sqlalchemy import Column, UUID, String
from sqlalchemy.orm import relationship
from core.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    users = relationship("User", back_populates="role")
