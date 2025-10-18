"""
Document model for knowledge base
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Document(Base):
    """Knowledge base document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Document details
    title = Column(String(500), nullable=False)
    path = Column(String(1000), nullable=False)  # File path in knowledge base
    content = Column(Text, nullable=False)
    
    # Document metadata
    file_type = Column(String(50), default="markdown")  # markdown, html, text
    file_size = Column(Integer)  # Size in bytes
    checksum = Column(String(64))  # File hash for change detection
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processed, error
    processed_at = Column(DateTime)
    
    # Analysis results
    analysis_results = Column(JSON)  # Gap analysis results
    gap_count = Column(Integer, default=0)
    question_count = Column(Integer, default=0)
    
    # Vector search
    is_indexed = Column(Boolean, default=False)
    embedding_model = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    gaps = relationship("Gap", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, path={self.path})>"
