"""
Gap model for knowledge gaps
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class GapType(str, enum.Enum):
    """Types of knowledge gaps"""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    ESG_COMPLIANCE = "esg_compliance"
    INCOMPLETE = "incomplete"
    MISSING = "missing"

class GapSeverity(str, enum.Enum):
    """Gap severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Gap(Base):
    """Knowledge gap model"""
    __tablename__ = "gaps"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Gap details
    type = Column(Enum(GapType), nullable=False)
    severity = Column(Enum(GapSeverity), nullable=False)
    location = Column(String(500), nullable=False)  # Section or line number
    description = Column(Text, nullable=False)
    
    # Context and metadata
    context = Column(JSON)  # Additional context data
    detected_by = Column(String(100), default="llm_orchestrator")
    
    # Status tracking
    status = Column(String(50), default="open")  # open, in_progress, resolved
    resolved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="gaps")
    questions = relationship("Question", back_populates="gap", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Gap(id={self.id}, type={self.type}, severity={self.severity})>"
