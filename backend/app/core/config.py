"""
Configuration settings for KT-AI Backend
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql+asyncpg://kt_user:kt_password@localhost:5432/kt_ai"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # LLM API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Azure OpenAI
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: Optional[str] = None
    
    # Azure AI Search
    azure_search_endpoint: str = "https://your-search-service.search.windows.net"
    azure_search_key: Optional[str] = None
    azure_search_index_name: str = "kt-ai-knowledge-base"
    azure_search_api_version: str = "2023-11-01"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: list = ["http://localhost:3000"]
    
    # LLM Settings
    default_model: str = "gpt-4-turbo-preview"
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # Cache Settings
    cache_ttl: int = 3600  # 1 hour
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
