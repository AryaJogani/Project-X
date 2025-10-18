"""
Azure OpenAI Provider for GPT models and embeddings
"""

from typing import Dict, Any, AsyncGenerator, List
import openai
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class AzureOpenAIProvider:
    """
    Azure OpenAI API provider for GPT models and embeddings
    """
    
    def __init__(self):
        self.client = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Azure OpenAI client"""
        if self.initialized:
            return
            
        if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
            raise ValueError("Azure OpenAI endpoint and API key not configured")
        
        try:
            self.client = openai.AsyncAzureOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version
            )
            
            # Test connection
            await self.client.models.list()
            
            self.initialized = True
            logger.info("✓ Azure OpenAI provider initialized")
            
        except Exception as e:
            logger.error(f"❌ Azure OpenAI provider initialization failed: {e}")
            raise
    
    async def generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate text using Azure OpenAI API
        
        Args:
            model: Model deployment name
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Returns:
            Response dictionary
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use deployment name if provided, otherwise use model name
            deployment_name = settings.azure_openai_deployment_name or model
            
            response = await self.client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            usage = response.usage
            
            return {
                "content": content,
                "tokens": usage.total_tokens,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "model": model,
                "provider": "azure_openai"
            }
            
        except Exception as e:
            logger.error(f"Azure OpenAI generation error: {e}")
            raise
    
    async def stream_generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream text generation using Azure OpenAI API
        
        Args:
            model: Model deployment name
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Yields:
            Streaming response chunks
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use deployment name if provided, otherwise use model name
            deployment_name = settings.azure_openai_deployment_name or model
            
            stream = await self.client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield {
                        "content": chunk.choices[0].delta.content,
                        "model": model,
                        "provider": "azure_openai"
                    }
                    
        except Exception as e:
            logger.error(f"Azure OpenAI streaming error: {e}")
            raise
    
    async def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-large"
    ) -> List[float]:
        """
        Generate embedding using Azure OpenAI API
        
        Args:
            text: Text to embed
            model: Embedding model deployment name
            
        Returns:
            Embedding vector
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use deployment name for embeddings
            deployment_name = settings.azure_openai_deployment_name or model
            
            response = await self.client.embeddings.create(
                model=deployment_name,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Azure OpenAI embedding error: {e}")
            raise
    
    async def generate_embeddings_batch(
        self,
        texts: List[str],
        model: str = "text-embedding-3-large"
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            model: Embedding model deployment name
            
        Returns:
            List of embedding vectors
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use deployment name for embeddings
            deployment_name = settings.azure_openai_deployment_name or model
            
            response = await self.client.embeddings.create(
                model=deployment_name,
                input=texts
            )
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            logger.error(f"Azure OpenAI batch embedding error: {e}")
            raise
    
    async def get_available_models(self) -> List[str]:
        """
        Get list of available models from Azure OpenAI
        
        Returns:
            List of available model names
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data]
            
        except Exception as e:
            logger.error(f"Azure OpenAI models list error: {e}")
            return []
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model
        
        Args:
            model: Model name
            
        Returns:
            Model information
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            model_info = await self.client.models.retrieve(model)
            return {
                "id": model_info.id,
                "object": model_info.object,
                "created": model_info.created,
                "owned_by": model_info.owned_by
            }
            
        except Exception as e:
            logger.error(f"Azure OpenAI model info error: {e}")
            return {}
