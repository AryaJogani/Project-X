"""
Answer Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AnswerBase(BaseModel):
    """Base answer schema"""
    content: str = Field(..., description="Answer content")
    answer_type: str = Field("text", description="Answer type")
    is_valid: bool = Field(True, description="Whether answer is valid")

class AnswerCreate(AnswerBase):
    """Schema for creating an answer"""
    question_id: int

class AnswerUpdate(BaseModel):
    """Schema for updating an answer"""
    content: Optional[str] = None
    answer_type: Optional[str] = None
    is_valid: Optional[bool] = None
    validation_notes: Optional[str] = None

class AnswerResponse(AnswerBase):
    """Schema for answer responses"""
    id: int
    question_id: int
    status: str
    processed_at: Optional[datetime] = None
    processed_by: str
    processing_context: Optional[Dict[str, Any]] = None
    validation_notes: Optional[str] = None
    confidence_score: Optional[str] = None
    relevance_score: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AnswerProcessingRequest(BaseModel):
    """Schema for answer processing requests"""
    answer_id: int
    processing_options: Optional[Dict[str, Any]] = None

class AnswerProcessingResponse(BaseModel):
    """Schema for answer processing responses"""
    answer_id: int
    processed_content: str
    confidence_score: float
    relevance_score: float
    processing_time: float
    status: str
