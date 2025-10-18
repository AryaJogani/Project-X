"""
Answer model for user responses
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Answer(Base):
    """User answer model"""
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Answer content
    content = Column(Text, nullable=False)
    answer_type = Column(String(50), default="text")  # text, number, date, list, table
    
    # Processing status
    status = Column(String(50), default="submitted")  # submitted, processed, validated
    processed_at = Column(DateTime)
    
    # LLM processing
    processed_by = Column(String(100), default="llm_orchestrator")
    processing_context = Column(JSON)  # Context used for processing
    
    # Validation
    is_valid = Column(Boolean, default=True)
    validation_notes = Column(Text)
    
    # Quality metrics
    confidence_score = Column(String(10))  # LLM confidence in answer quality
    relevance_score = Column(String(10))   # Relevance to the question
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    question = relationship("Question", back_populates="answers")
    
    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id}, status={self.status})>"
