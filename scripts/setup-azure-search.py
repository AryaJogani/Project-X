#!/usr/bin/env python3
"""
Azure AI Search Setup Script
Creates and configures Azure AI Search index for KT-AI
"""

import os
import sys
import asyncio
import logging
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticSearch,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_azure_search():
    """Setup Azure AI Search index"""
    
    try:
        # Initialize credentials
        if settings.azure_search_key:
            credential = AzureKeyCredential(settings.azure_search_key)
            logger.info("Using API key authentication")
        else:
            credential = DefaultAzureCredential()
            logger.info("Using Azure Identity authentication")
        
        # Initialize search client
        index_client = SearchIndexClient(
            endpoint=settings.azure_search_endpoint,
            credential=credential
        )
        
        # Check if index exists
        try:
            existing_index = index_client.get_index(settings.azure_search_index_name)
            logger.info(f"Index '{settings.azure_search_index_name}' already exists")
            return
        except Exception:
            logger.info(f"Index '{settings.azure_search_index_name}' does not exist, creating...")
        
        # Define the index schema
        index = SearchIndex(
            name=settings.azure_search_index_name,
            fields=[
                SimpleField(name="id", type="Edm.String", key=True),
                SimpleField(name="document_id", type="Edm.String", filterable=True),
                SearchableField(name="content", type="Edm.String", analyzer_name="en.microsoft"),
                SimpleField(name="title", type="Edm.String", searchable=True),
                SimpleField(name="path", type="Edm.String", filterable=True),
                SimpleField(name="file_type", type="Edm.String", filterable=True),
                SimpleField(name="chunk_index", type="Edm.Int32", filterable=True),
                SimpleField(name="created_at", type="Edm.DateTimeOffset", filterable=True, sortable=True),
                SimpleField(name="updated_at", type="Edm.DateTimeOffset", filterable=True, sortable=True),
                # Vector field for embeddings
                SearchableField(
                    name="content_vector",
                    type="Collection(Edm.Single)",
                    vector_search_dimensions=1536,  # OpenAI embedding dimensions
                    vector_search_profile_name="default-vector-profile"
                )
            ],
            vector_search=VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="default-algorithm",
                        parameters={
                            "m": 4,
                            "efConstruction": 400,
                            "efSearch": 500
                        }
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        name="default-vector-profile",
                        algorithm="default-algorithm"
                    )
                ]
            ),
            semantic_search=SemanticSearch(
                configurations=[
                    SemanticConfiguration(
                        name="default-semantic-config",
                        prioritized_fields=SemanticPrioritizedFields(
                            title_field=SemanticField(field_name="title"),
                            content_fields=[
                                SemanticField(field_name="content")
                            ]
                        )
                    )
                ]
            )
        )
        
        # Create the index
        index_client.create_index(index)
        logger.info(f"✅ Successfully created Azure AI Search index: {settings.azure_search_index_name}")
        
        # Wait for index to be ready
        logger.info("⏳ Waiting for index to be ready...")
        await asyncio.sleep(10)
        
        # Verify index creation
        try:
            created_index = index_client.get_index(settings.azure_search_index_name)
            logger.info(f"✅ Index verified: {created_index.name}")
            logger.info(f"   Fields: {len(created_index.fields)}")
            logger.info(f"   Vector search: {created_index.vector_search is not None}")
            logger.info(f"   Semantic search: {created_index.semantic_search is not None}")
        except Exception as e:
            logger.error(f"❌ Failed to verify index: {e}")
            raise
        
    except Exception as e:
        logger.error(f"❌ Azure AI Search setup failed: {e}")
        raise

async def main():
    """Main setup function"""
    logger.info("🚀 Setting up Azure AI Search for KT-AI...")
    
    # Check required environment variables
    required_vars = [
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_INDEX_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file or environment")
        sys.exit(1)
    
    # Check if we have either API key or Azure Identity
    if not settings.azure_search_key:
        logger.warning("⚠️  No AZURE_SEARCH_KEY provided, using Azure Identity authentication")
        logger.warning("Make sure you're logged in with 'az login' or have managed identity configured")
    
    try:
        await setup_azure_search()
        logger.info("🎉 Azure AI Search setup completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Update your .env file with Azure AI Search credentials")
        logger.info("2. Start the backend application")
        logger.info("3. Test the vector search functionality")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
