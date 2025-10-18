"""
Gap Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.gap import GapType, GapSeverity

class GapBase(BaseModel):
    """Base gap schema"""
    type: GapType
    severity: GapSeverity
    location: str = Field(..., description="Section or line number")
    description: str = Field(..., description="Gap description")
    context: Optional[Dict[str, Any]] = None

class GapCreate(GapBase):
    """Schema for creating a gap"""
    document_id: int

class GapUpdate(BaseModel):
    """Schema for updating a gap"""
    type: Optional[GapType] = None
    severity: Optional[GapSeverity] = None
    location: Optional[str] = None
    description: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class GapResponse(GapBase):
    """Schema for gap responses"""
    id: int
    document_id: int
    status: str
    detected_by: str
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class GapAnalysisRequest(BaseModel):
    """Schema for gap analysis requests"""
    document_id: int
    analysis_type: str = "comprehensive"  # comprehensive, structural, semantic, esg
    options: Optional[Dict[str, Any]] = None

class GapAnalysisResponse(BaseModel):
    """Schema for gap analysis responses"""
    document_id: int
    analysis_type: str
    gaps_found: int
    gaps: list[GapResponse]
    analysis_time: float
    status: str
