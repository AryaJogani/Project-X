"""
Google Provider for Gemini models
"""

from typing import Dict, Any, AsyncGenerator
import google.generativeai as genai
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class GoogleProvider:
    """
    Google API provider for Gemini models
    """
    
    def __init__(self):
        self.model = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Google client"""
        if self.initialized:
            return
            
        if not settings.google_api_key:
            raise ValueError("Google API key not configured")
        
        try:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            
            self.initialized = True
            logger.info("✓ Google provider initialized")
            
        except Exception as e:
            logger.error(f"❌ Google provider initialization failed: {e}")
            raise
    
    async def generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate text using Google API
        
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
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            content = response.text
            
            return {
                "content": content,
                "tokens": len(prompt.split()) + len(content.split()),  # Approximate
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(content.split()),
                "model": model,
                "provider": "google"
            }
            
        except Exception as e:
            logger.error(f"Google generation error: {e}")
            raise
    
    async def stream_generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream text generation using Google API
        
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
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
            
            # Note: Google's Gemini doesn't support true streaming yet
            # We'll simulate streaming by chunking the response
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            content = response.text
            
            # Simulate streaming by chunking
            words = content.split()
            chunk_size = max(1, len(words) // 10)  # 10 chunks
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                if chunk.strip():
                    yield {
                        "content": chunk + " ",
                        "model": model,
                        "provider": "google"
                    }
                    
        except Exception as e:
            logger.error(f"Google streaming error: {e}")
            raise
