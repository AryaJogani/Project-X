"""
Anthropic Provider for Claude models
"""

from typing import Dict, Any, AsyncGenerator
import anthropic
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class AnthropicProvider:
    """
    Anthropic API provider for Claude models
    """
    
    def __init__(self):
        self.client = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Anthropic client"""
        if self.initialized:
            return
            
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        try:
            self.client = anthropic.AsyncAnthropic(
                api_key=settings.anthropic_api_key
            )
            
            self.initialized = True
            logger.info("✓ Anthropic provider initialized")
            
        except Exception as e:
            logger.error(f"❌ Anthropic provider initialization failed: {e}")
            raise
    
    async def generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate text using Anthropic API
        
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
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            usage = response.usage
            
            return {
                "content": content,
                "tokens": usage.input_tokens + usage.output_tokens,
                "prompt_tokens": usage.input_tokens,
                "completion_tokens": usage.output_tokens,
                "model": model,
                "provider": "anthropic"
            }
            
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise
    
    async def stream_generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream text generation using Anthropic API
        
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
            stream = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            async for chunk in stream:
                if hasattr(chunk, 'delta') and chunk.delta.text:
                    yield {
                        "content": chunk.delta.text,
                        "model": model,
                        "provider": "anthropic"
                    }
                    
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise
