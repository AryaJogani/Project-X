#!/usr/bin/env python3
"""
Azure OpenAI Setup Script
Configures Azure OpenAI for KT-AI LLM orchestration
"""

import os
import sys
import asyncio
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import CognitiveServicesAccount, Sku

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_azure_openai():
    """Setup Azure OpenAI service"""
    
    try:
        # Check if Azure OpenAI is configured
        if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
            logger.error("❌ Azure OpenAI not configured")
            logger.error("Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in your .env file")
            return False
        
        # Test Azure OpenAI connection
        from app.llm.providers.azure_openai_provider import AzureOpenAIProvider
        
        provider = AzureOpenAIProvider()
        await provider.initialize()
        
        # Test model availability
        models = await provider.get_available_models()
        logger.info(f"✅ Azure OpenAI connected successfully")
        logger.info(f"Available models: {len(models)}")
        
        # Test embedding generation
        test_embedding = await provider.generate_embedding(
            text="Test embedding generation",
            model="text-embedding-3-large"
        )
        
        logger.info(f"✅ Embeddings working: {len(test_embedding)} dimensions")
        
        # Test text generation
        test_response = await provider.generate(
            model="gpt-3.5-turbo",
            prompt="Hello, this is a test.",
            max_tokens=10
        )
        
        logger.info(f"✅ Text generation working: {test_response['content'][:50]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Azure OpenAI setup failed: {e}")
        return False

async def check_azure_openai_deployment():
    """Check Azure OpenAI deployment status"""
    
    try:
        logger.info("🔍 Checking Azure OpenAI deployment...")
        
        # This would require Azure Resource Manager permissions
        # For now, we'll just test the API connection
        from app.llm.providers.azure_openai_provider import AzureOpenAIProvider
        
        provider = AzureOpenAIProvider()
        await provider.initialize()
        
        # Get model information
        if settings.azure_openai_deployment_name:
            model_info = await provider.get_model_info(settings.azure_openai_deployment_name)
            if model_info:
                logger.info(f"✅ Deployment '{settings.azure_openai_deployment_name}' is available")
                logger.info(f"   Model ID: {model_info.get('id', 'Unknown')}")
                logger.info(f"   Created: {model_info.get('created', 'Unknown')}")
            else:
                logger.warning(f"⚠️  Deployment '{settings.azure_openai_deployment_name}' not found")
        else:
            logger.warning("⚠️  No deployment name configured")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Azure OpenAI deployment check failed: {e}")
        return False

async def test_llm_orchestration():
    """Test LLM orchestration with Azure OpenAI"""
    
    try:
        logger.info("🧠 Testing LLM orchestration...")
        
        from app.llm.orchestrator import LLMOrchestrator
        
        orchestrator = LLMOrchestrator()
        await orchestrator.initialize()
        
        # Test different task types
        test_tasks = [
            ("gap_classification", "Classify this ESG gap: missing sustainability metrics"),
            ("question_generation", "Generate questions for ESG compliance gap"),
            ("semantic_embedding", "Generate embedding for: environmental impact assessment")
        ]
        
        for task_type, prompt in test_tasks:
            try:
                response = await orchestrator.generate(
                    task_type=task_type,
                    prompt=prompt,
                    max_tokens=100
                )
                
                logger.info(f"✅ {task_type}: {response['content'][:50]}...")
                
            except Exception as e:
                logger.warning(f"⚠️  {task_type} failed: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ LLM orchestration test failed: {e}")
        return False

async def main():
    """Main setup function"""
    logger.info("🚀 Setting up Azure OpenAI for KT-AI...")
    
    # Check required environment variables
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file or environment")
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Azure OpenAI Connection", setup_azure_openai),
        ("Deployment Check", check_azure_openai_deployment),
        ("LLM Orchestration Test", test_llm_orchestration)
    ]
    
    all_passed = True
    
    for step_name, step_func in steps:
        logger.info(f"\n📋 {step_name}...")
        try:
            result = await step_func()
            if result:
                logger.info(f"✅ {step_name} completed successfully")
            else:
                logger.error(f"❌ {step_name} failed")
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {step_name} failed with error: {e}")
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 Azure OpenAI setup completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Start the backend application")
        logger.info("2. Test the gap detection functionality")
        logger.info("3. Test the question generation")
        logger.info("4. Monitor LLM usage and costs")
        
    else:
        logger.error("\n❌ Azure OpenAI setup failed")
        logger.error("Please check your configuration and try again")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
