from uuid import uuid4
from enum import Enum
from core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import LtreeType
from sqlalchemy import Column, UUID, String, ForeignKey, Table, DateTime, func, event, select
from sqlalchemy.orm import object_session

folder_department_permissions = Table(
    "folder_department_permissions",
    Base.metadata,
    Column("folder_id", UUID, ForeignKey("folders.id", ondelete="CASCADE"), primary_key=True),
    Column("department_id", UUID, ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_level", String(50), default="read", nullable=False),
)

folder_user_permissions = Table(
    "folder_user_permissions",
    Base.metadata,
    Column("folder_id", UUID, ForeignKey("folders.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_level", String(50), default="read", nullable=False),
)

class AccessMode(str, Enum):
    PRIVATE = "private"
    INHERITED = "inherited"
    PUBLIC = "public"


class Folder(Base):
    __tablename__ = "folders"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    path = Column(LtreeType, nullable=False, index=True)

    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True)
    category = relationship("Category", back_populates="folders")
    documents = relationship("Document", back_populates="folder", cascade="all, delete-orphan")

    parent = relationship("Folder", remote_side=[id], back_populates="children")
    parent_id = Column(UUID(as_uuid=True), ForeignKey("folders.id", ondelete="CASCADE"), nullable=True, index=True)
    children = relationship("Folder", back_populates="parent", cascade="all, delete-orphan")
    access_mode = Column(String(50), default=AccessMode.PRIVATE, nullable=False, index=True)

    allowed_users = relationship("User", secondary=folder_user_permissions, back_populates="accessible_folders")
    allowed_departments = relationship(
        "Department", secondary=folder_department_permissions, back_populates="accessible_folders"
    )


@event.listens_for(Folder, "before_insert")
@event.listens_for(Folder, "before_update")
def generate_path(mapper, connection, target):
    if target.parent_id:
        session = object_session(target)
        if session is not None:
            parent = session.query(Folder).filter(Folder.id == target.parent_id).first()
            if parent:
                target.path = f"{parent.path}.{target.id}"
        else:
            parent_row = connection.execute(select(Folder.path).where(Folder.id == target.parent_id)).fetchone()
            if parent_row and parent_row[0] is not None:
                target.path = f"{parent_row[0]}.{target.id}"
    else:
        target.path = str(target.id)
