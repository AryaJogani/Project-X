"""
Document Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DocumentBase(BaseModel):
    """Base document schema"""
    title: str = Field(..., description="Document title")
    path: str = Field(..., description="File path in knowledge base")
    content: str = Field(..., description="Document content")
    file_type: str = Field("markdown", description="File type")
    file_size: Optional[int] = Field(None, description="File size in bytes")

class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    pass

class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = None
    content: Optional[str] = None
    file_type: Optional[str] = None
    status: Optional[str] = None

class DocumentResponse(DocumentBase):
    """Schema for document responses"""
    id: int
    checksum: Optional[str] = None
    status: str
    processed_at: Optional[datetime] = None
    analysis_results: Optional[Dict[str, Any]] = None
    gap_count: int = 0
    question_count: int = 0
    is_indexed: bool = False
    embedding_model: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentUploadRequest(BaseModel):
    """Schema for document upload requests"""
    file_name: str
    file_content: str
    file_type: str = "markdown"
    metadata: Optional[Dict[str, Any]] = None

class DocumentUploadResponse(BaseModel):
    """Schema for document upload responses"""
    document_id: int
    file_name: str
    status: str
    message: str

class DocumentSearchRequest(BaseModel):
    """Schema for document search requests"""
    query: str
    n_results: int = 10
    filters: Optional[Dict[str, Any]] = None

class DocumentSearchResponse(BaseModel):
    """Schema for document search responses"""
    query: str
    results: list[DocumentResponse]
    total: int
    search_time: float
