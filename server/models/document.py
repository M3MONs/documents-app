from sqlalchemy import Column, Index, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from enum import Enum
from core.database import Base

class FileType(str, Enum):
    PNG = "image/png"
    JPG = "image/jpeg"
    JPEG = "image/jpeg"
    GIF = "image/gif"
    WEBP = "image/webp"
    PDF = "application/pdf"
    TXT = "text/plain"
    CSV = "text/csv"
    ZIP = "application/zip"
    
VIEWABLE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "application/pdf",
    "text/plain",
}

class SyncStatus(str, Enum):
    SYNCED = "synced"
    MODIFIED = "modified"

class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index('unique_folder_name', 'folder_id', 'name', unique=True),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(BigInteger, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)
    sync_status = Column(String(50), default=SyncStatus.SYNCED, nullable=False, index=True)

    category_id = Column(UUID(as_uuid=True), 
                       ForeignKey("categories.id", ondelete="CASCADE"), 
                       nullable=True, 
                       index=True)
    category = relationship("Category", back_populates="documents")

    folder_id = Column(UUID(as_uuid=True), 
                       ForeignKey("folders.id", ondelete="CASCADE"), 
                       nullable=True, 
                       index=True)
    folder = relationship("Folder", back_populates="documents")
    
    def is_viewable(self) -> bool:
        return self.mime_type in VIEWABLE_MIME_TYPES