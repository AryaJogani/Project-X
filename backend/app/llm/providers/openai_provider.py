"""
OpenAI Provider for GPT models
"""

from typing import Dict, Any, AsyncGenerator
import openai
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIProvider:
    """
    OpenAI API provider for GPT models
    """
    
    def __init__(self):
        self.client = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize OpenAI client"""
        if self.initialized:
            return
            
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            self.client = openai.AsyncOpenAI(
                api_key=settings.openai_api_key
            )
            
            # Test connection
            await self.client.models.list()
            
            self.initialized = True
            logger.info("✓ OpenAI provider initialized")
            
        except Exception as e:
            logger.error(f"❌ OpenAI provider initialization failed: {e}")
            raise
    
    async def generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate text using OpenAI API
        
        Args:
            model: Model to use
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Returns:
            Response dictionary
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
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
                "provider": "openai"
            }
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def stream_generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream text generation using OpenAI API
        
        Args:
            model: Model to use
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Yields:
            Streaming response chunks
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
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
                        "provider": "openai"
                    }
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
    
    async def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-large"
    ) -> list:
        """
        Generate embedding using OpenAI API
        
        Args:
            text: Text to embed
            model: Embedding model to use
            
        Returns:
            Embedding vector
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
