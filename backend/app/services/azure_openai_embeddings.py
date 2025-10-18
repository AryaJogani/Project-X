"""
Azure OpenAI Embeddings Service
Handles embedding generation using Azure OpenAI
"""

from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings
from app.llm.providers.azure_openai_provider import AzureOpenAIProvider

logger = logging.getLogger(__name__)

class AzureOpenAIEmbeddingsService:
    """
    Azure OpenAI embeddings service for vector operations
    """
    
    def __init__(self):
        self.azure_openai = AzureOpenAIProvider()
        self.initialized = False
    
    async def initialize(self):
        """Initialize Azure OpenAI provider"""
        if self.initialized:
            return
            
        try:
            await self.azure_openai.initialize()
            self.initialized = True
            logger.info("✓ Azure OpenAI embeddings service initialized")
            
        except Exception as e:
            logger.error(f"❌ Azure OpenAI embeddings initialization failed: {e}")
            raise
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-3-large"
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of texts to embed
            model: Embedding model to use
            
        Returns:
            List of embedding vectors
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Generate embeddings using Azure OpenAI
            embeddings = await self.azure_openai.generate_embeddings_batch(
                texts=texts,
                model=model
            )
            
            logger.info(f"Generated {len(embeddings)} embeddings using Azure OpenAI")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embeddings generation error: {e}")
            raise
    
    async def generate_single_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-large"
    ) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            model: Embedding model to use
            
        Returns:
            Embedding vector
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Generate embedding using Azure OpenAI
            embedding = await self.azure_openai.generate_embedding(
                text=text,
                model=model
            )
            
            return embedding
            
        except Exception as e:
            logger.error(f"Single embedding generation error: {e}")
            raise
    
    async def get_embedding_dimensions(self, model: str = "text-embedding-3-large") -> int:
        """
        Get the dimensions of embeddings for a model
        
        Args:
            model: Embedding model name
            
        Returns:
            Number of dimensions
        """
        
        # Azure OpenAI embedding dimensions
        model_dimensions = {
            "text-embedding-3-large": 3072,
            "text-embedding-3-small": 1536,
            "text-embedding-ada-002": 1536
        }
        
        return model_dimensions.get(model, 1536)
    
    async def validate_embeddings(
        self,
        embeddings: List[List[float]],
        expected_dimensions: int = 1536
    ) -> bool:
        """
        Validate embeddings format and dimensions
        
        Args:
            embeddings: List of embedding vectors
            expected_dimensions: Expected number of dimensions
            
        Returns:
            True if valid, False otherwise
        """
        
        if not embeddings:
            return False
        
        for embedding in embeddings:
            if not isinstance(embedding, list):
                return False
            if len(embedding) != expected_dimensions:
                return False
            if not all(isinstance(x, (int, float)) for x in embedding):
                return False
        
        return True
    
    async def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Get embedding service statistics
        
        Returns:
            Service statistics
        """
        
        return {
            "provider": "azure_openai",
            "initialized": self.initialized,
            "endpoint": settings.azure_openai_endpoint,
            "api_version": settings.azure_openai_api_version,
            "deployment_name": settings.azure_openai_deployment_name
        }
