"""
Redis cache configuration and utilities
"""

import redis.asyncio as redis
from app.core.config import settings
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Create Redis client
redis_client = redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True
)

class CacheManager:
    """Redis cache manager with utility methods"""
    
    def __init__(self):
        self.client = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = None
    ) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or settings.cache_ttl
            serialized = json.dumps(value)
            await self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0

# Global cache manager instance
cache_manager = CacheManager()
