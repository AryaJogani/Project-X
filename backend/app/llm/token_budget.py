"""
Token Budget Manager for cost control and optimization
"""

from typing import Dict, Any
import asyncio
import logging
from datetime import datetime, timedelta

from app.core.cache import cache_manager
from app.core.config import settings

logger = logging.getLogger(__name__)

class TokenBudgetManager:
    """
    Manage token usage and costs across LLM calls
    """
    
    def __init__(self, daily_budget: int = 100000):
        self.daily_budget = daily_budget
        self.current_usage = 0
        self.usage_by_model = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize budget manager"""
        if self.initialized:
            return
            
        try:
            # Load current usage from cache
            today = datetime.now().strftime("%Y-%m-%d")
            usage_key = f"token_usage:{today}"
            
            cached_usage = await cache_manager.get(usage_key)
            if cached_usage:
                self.current_usage = cached_usage.get("total", 0)
                self.usage_by_model = cached_usage.get("by_model", {})
            
            self.initialized = True
            logger.info(f"✓ Token budget initialized: {self.current_usage}/{self.daily_budget}")
            
        except Exception as e:
            logger.error(f"❌ Token budget initialization failed: {e}")
            raise
    
    async def check_and_allocate(
        self,
        estimated_tokens: int,
        priority: str = "normal",
        model: str = "unknown"
    ) -> bool:
        """
        Check if we have budget for this request
        
        Args:
            estimated_tokens: Estimated tokens for the request
            priority: Request priority (low, normal, high)
            model: Model being used
            
        Returns:
            True if request can proceed
            
        Raises:
            TokenBudgetExceeded: If budget is exceeded
        """
        
        if not self.initialized:
            await self.initialize()
        
        # Check if we're over budget
        if self.current_usage + estimated_tokens > self.daily_budget:
            if priority == "high":
                logger.warning("Over budget but allowing high priority request")
            else:
                raise TokenBudgetExceeded(
                    f"Daily budget exceeded: {self.current_usage}/{self.daily_budget}"
                )
        
        # Reserve tokens
        self.current_usage += estimated_tokens
        self.usage_by_model[model] = self.usage_by_model.get(model, 0) + estimated_tokens
        
        # Update cache
        await self._update_usage_cache()
        
        return True
    
    async def record_usage(
        self,
        actual_tokens: int,
        model: str,
        cost: float = 0.0
    ):
        """
        Record actual token usage after completion
        
        Args:
            actual_tokens: Actual tokens used
            model: Model used
            cost: Cost in dollars
        """
        
        # Update usage
        self.current_usage += actual_tokens
        self.usage_by_model[model] = self.usage_by_model.get(model, 0) + actual_tokens
        
        # Update cache
        await self._update_usage_cache()
        
        # Log usage
        logger.info(f"Token usage recorded: {actual_tokens} tokens, {cost:.4f} cost")
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current usage statistics
        
        Returns:
            Usage statistics
        """
        
        if not self.initialized:
            await self.initialize()
        
        return {
            "daily_budget": self.daily_budget,
            "current_usage": self.current_usage,
            "remaining": self.daily_budget - self.current_usage,
            "usage_percentage": (self.current_usage / self.daily_budget) * 100,
            "by_model": self.usage_by_model,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _update_usage_cache(self):
        """Update usage in cache"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            usage_key = f"token_usage:{today}"
            
            usage_data = {
                "total": self.current_usage,
                "by_model": self.usage_by_model,
                "updated_at": datetime.now().isoformat()
            }
            
            await cache_manager.set(usage_key, usage_data, ttl=86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Failed to update usage cache: {e}")
    
    async def reset_daily_budget(self):
        """Reset daily budget (called at midnight)"""
        self.current_usage = 0
        self.usage_by_model = {}
        await self._update_usage_cache()
        logger.info("Daily token budget reset")
    
    async def shutdown(self):
        """Shutdown budget manager"""
        try:
            await self._update_usage_cache()
            logger.info("✓ Token budget manager shutdown complete")
        except Exception as e:
            logger.error(f"❌ Token budget shutdown error: {e}")

class TokenBudgetExceeded(Exception):
    """Exception raised when token budget is exceeded"""
    pass
