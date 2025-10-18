"""
LLM Provider implementations
"""

from typing import Dict, Any, AsyncGenerator
import asyncio
import logging

logger = logging.getLogger(__name__)

async def get_all_providers() -> Dict[str, Any]:
    """
    Initialize all available LLM providers
    
    Returns:
        Dictionary of provider_name -> provider_instance
    """
    providers = {}
    
    try:
        # OpenAI Provider
        from .openai_provider import OpenAIProvider
        providers["openai"] = OpenAIProvider()
        await providers["openai"].initialize()
        logger.info("✓ OpenAI provider initialized")
    except Exception as e:
        logger.warning(f"⚠ OpenAI provider failed: {e}")
    
    try:
        # Azure OpenAI Provider
        from .azure_openai_provider import AzureOpenAIProvider
        providers["azure_openai"] = AzureOpenAIProvider()
        await providers["azure_openai"].initialize()
        logger.info("✓ Azure OpenAI provider initialized")
    except Exception as e:
        logger.warning(f"⚠ Azure OpenAI provider failed: {e}")
    
    try:
        # Anthropic Provider
        from .anthropic_provider import AnthropicProvider
        providers["anthropic"] = AnthropicProvider()
        await providers["anthropic"].initialize()
        logger.info("✓ Anthropic provider initialized")
    except Exception as e:
        logger.warning(f"⚠ Anthropic provider failed: {e}")
    
    try:
        # Google Provider
        from .google_provider import GoogleProvider
        providers["google"] = GoogleProvider()
        await providers["google"].initialize()
        logger.info("✓ Google provider initialized")
    except Exception as e:
        logger.warning(f"⚠ Google provider failed: {e}")
    
    if not providers:
        raise RuntimeError("No LLM providers available")
    
    return providers
