"""
LLM Orchestration Controller
Central intelligence for multi-model LLM routing and optimization
"""

from typing import Optional, Dict, Any, List, AsyncGenerator
import json
import hashlib
import logging
from datetime import datetime

from app.core.config import settings
from app.core.cache import cache_manager
from app.llm.router import ModelRouter
from app.llm.token_budget import TokenBudgetManager

logger = logging.getLogger(__name__)

class LLMOrchestrator:
    """
    Central LLM orchestration controller
    """
    
    def __init__(self):
        self.router = ModelRouter()
        self.cache = cache_manager
        self.token_budget = TokenBudgetManager()
        self.providers = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize LLM providers and components"""
        if self.initialized:
            return
            
        try:
            # Initialize providers
            from app.llm.providers import get_all_providers
            self.providers = await get_all_providers()
            
            # Initialize token budget
            await self.token_budget.initialize()
            
            self.initialized = True
            logger.info("✓ LLM Orchestrator initialized")
            
        except Exception as e:
            logger.error(f"❌ LLM Orchestrator initialization failed: {e}")
            raise
    
    async def generate(
        self,
        task_type: str,
        prompt: str,
        context: Optional[Dict] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Main LLM generation method with intelligent routing
        
        Args:
            task_type: Type of task (gap_analysis, question_gen, etc.)
            prompt: The prompt text
            context: Additional context
            max_tokens: Max tokens to generate
            temperature: Generation temperature
            stream: Whether to stream response
            
        Returns:
            LLM response with metadata
        """
        
        if not self.initialized:
            await self.initialize()
        
        # 1. Check token budget
        estimated_tokens = len(prompt.split()) * 2  # Rough estimate
        await self.token_budget.check_and_allocate(
            estimated_tokens,
            priority="normal"
        )
        
        # 2. Check cache
        cache_key = self._generate_cache_key(task_type, prompt, context)
        cached_response = await self.cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for task: {task_type}")
            return {
                "content": cached_response,
                "cached": True,
                "tokens": 0,
                "cost": 0,
                "model": "cached"
            }
        
        # 3. Route to appropriate model
        model_config = self.router.select_model(
            task_type=task_type,
            prompt_length=len(prompt),
            context=context
        )
        
        # 4. Get provider
        provider = self.providers.get(model_config["provider"])
        if not provider:
            raise ValueError(f"Provider {model_config['provider']} not available")
        
        # 5. Generate response
        try:
            if stream:
                return provider.stream_generate(
                    model=model_config["model"],
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            else:
                response = await provider.generate(
                    model=model_config["model"],
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                # 6. Cache successful response
                await self.cache.set(
                    cache_key,
                    response["content"],
                    ttl=3600
                )
                
                return response
                
        except Exception as e:
            # 7. Try fallback model
            logger.warning(f"Primary model failed: {e}, using fallback")
            fallback_config = self.router.get_fallback(model_config)
            fallback_provider = self.providers.get(fallback_config["provider"])
            
            if not fallback_provider:
                raise ValueError("No fallback provider available")
            
            response = await fallback_provider.generate(
                model=fallback_config["model"],
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Cache fallback response
            await self.cache.set(
                cache_key,
                response["content"],
                ttl=1800  # Shorter TTL for fallback
            )
            
            return response
    
    async def generate_stream(
        self,
        task_type: str,
        prompt: str,
        context: Optional[Dict] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream LLM responses for real-time updates
        """
        
        if not self.initialized:
            await self.initialize()
        
        # Route to appropriate model
        model_config = self.router.select_model(
            task_type=task_type,
            prompt_length=len(prompt),
            context=context
        )
        
        # Get provider
        provider = self.providers.get(model_config["provider"])
        if not provider:
            raise ValueError(f"Provider {model_config['provider']} not available")
        
        # Stream response
        async for chunk in provider.stream_generate(
            model=model_config["model"],
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        ):
            yield chunk
    
    def _generate_cache_key(
        self,
        task_type: str,
        prompt: str,
        context: Optional[Dict]
    ) -> str:
        """Generate cache key for prompt"""
        context_str = json.dumps(context, sort_keys=True) if context else ""
        key_string = f"{task_type}:{prompt}:{context_str}"
        return f"llm:prompt:{hashlib.sha256(key_string.encode()).hexdigest()}"
    
    async def batch_generate(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple responses in parallel
        """
        import asyncio
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_limit(request):
            async with semaphore:
                return await self.generate(**request)
        
        # Process all requests concurrently
        results = await asyncio.gather(
            *[generate_with_limit(req) for req in requests],
            return_exceptions=True
        )
        
        return [r for r in results if not isinstance(r, Exception)]
    
    async def shutdown(self):
        """Shutdown orchestrator and cleanup"""
        try:
            await self.token_budget.shutdown()
            logger.info("✓ LLM Orchestrator shutdown complete")
        except Exception as e:
            logger.error(f"❌ LLM Orchestrator shutdown error: {e}")
