"""
Question Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class QuestionBase(BaseModel):
    """Base question schema"""
    level: int = Field(..., ge=1, le=4, description="Progressive disclosure level")
    content: str = Field(..., description="Question content")
    context: Optional[str] = Field(None, description="Additional context")
    answer_type: str = Field("text", description="Expected answer type")
    required: bool = Field(True, description="Whether question is required")
    depends_on: Optional[int] = Field(None, description="Previous question dependency")

class QuestionCreate(QuestionBase):
    """Schema for creating a question"""
    gap_id: int

class QuestionUpdate(BaseModel):
    """Schema for updating a question"""
    content: Optional[str] = None
    context: Optional[str] = None
    answer_type: Optional[str] = None
    required: Optional[bool] = None
    depends_on: Optional[int] = None
    status: Optional[str] = None

class QuestionResponse(QuestionBase):
    """Schema for question responses"""
    id: int
    gap_id: int
    status: str
    answered_at: Optional[datetime] = None
    generated_by: str
    generation_context: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QuestionGenerationRequest(BaseModel):
    """Schema for question generation requests"""
    gap_id: int
    context: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None

class QuestionGenerationResponse(BaseModel):
    """Schema for question generation responses"""
    gap_id: int
    questions_generated: int
    questions: list[QuestionResponse]
    generation_time: float
    status: str
