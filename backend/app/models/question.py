"""
Question model for progressive disclosure
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Question(Base):
    """Progressive disclosure question model"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    gap_id = Column(Integer, ForeignKey("gaps.id"), nullable=False)
    
    # Question details
    level = Column(Integer, nullable=False)  # 1-4 for progressive disclosure
    content = Column(Text, nullable=False)
    context = Column(Text)  # Additional context for the question
    
    # Answer configuration
    answer_type = Column(String(50), default="text")  # text, number, date, list, table
    required = Column(Boolean, default=True)
    depends_on = Column(Integer, ForeignKey("questions.id"))  # Previous question dependency
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, answered, skipped
    answered_at = Column(DateTime)
    
    # LLM metadata
    generated_by = Column(String(100), default="llm_orchestrator")
    generation_context = Column(JSON)  # Context used for generation
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    gap = relationship("Gap", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    depends_on_question = relationship("Question", remote_side=[id])
    
    def __repr__(self):
        return f"<Question(id={self.id}, level={self.level}, gap_id={self.gap_id})>"
