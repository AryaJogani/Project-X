#!/usr/bin/env python3
"""
Simplified Azure Setup Script for KT-AI
Interactive setup for Azure AI Search and Azure OpenAI
"""

import os
import sys
import json
import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and return the result"""
    try:
        logger.info(f"🔄 {description}...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ {description} completed")
            return result.stdout.strip()
        else:
            logger.error(f"❌ {description} failed: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"❌ {description} failed: {e}")
        return None

def check_azure_cli():
    """Check if Azure CLI is installed"""
    result = run_command("az --version", "Checking Azure CLI")
    if result:
        logger.info("✅ Azure CLI is installed")
        return True
    else:
        logger.error("❌ Azure CLI is not installed")
        logger.error("Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False

def login_azure():
    """Login to Azure"""
    result = run_command("az login", "Logging into Azure")
    if result:
        logger.info("✅ Logged into Azure")
        return True
    else:
        logger.error("❌ Failed to login to Azure")
        return False

def get_subscription():
    """Get current subscription"""
    result = run_command("az account show --query id -o tsv", "Getting current subscription")
    if result:
        logger.info(f"✅ Using subscription: {result}")
        return result
    else:
        logger.error("❌ No active subscription found")
        return None

def create_resource_group(resource_group_name, location):
    """Create resource group"""
    command = f"az group create --name {resource_group_name} --location {location}"
    result = run_command(command, f"Creating resource group '{resource_group_name}'")
    return result is not None

def create_azure_openai(resource_group_name, location):
    """Create Azure OpenAI resource"""
    openai_name = f"kt-ai-openai-{int(time.time())}"
    
    command = f"""az cognitiveservices account create \
        --name {openai_name} \
        --resource-group {resource_group_name} \
        --location {location} \
        --kind OpenAI \
        --sku S0"""
    
    result = run_command(command, f"Creating Azure OpenAI resource '{openai_name}'")
    if result:
        # Get the endpoint and key
        endpoint_cmd = f"az cognitiveservices account show --name {openai_name} --resource-group {resource_group_name} --query properties.endpoint -o tsv"
        key_cmd = f"az cognitiveservices account keys list --name {openai_name} --resource-group {resource_group_name} --query key1 -o tsv"
        
        endpoint = run_command(endpoint_cmd, "Getting Azure OpenAI endpoint")
        api_key = run_command(key_cmd, "Getting Azure OpenAI API key")
        
        if endpoint and api_key:
            return {
                'name': openai_name,
                'endpoint': endpoint,
                'api_key': api_key
            }
    
    return None

def create_azure_search(resource_group_name, location):
    """Create Azure AI Search resource"""
    search_name = f"kt-ai-search-{int(time.time())}"
    
    command = f"""az search service create \
        --name {search_name} \
        --resource-group {resource_group_name} \
        --location {location} \
        --sku standard \
        --partition-count 1 \
        --replica-count 1"""
    
    result = run_command(command, f"Creating Azure AI Search resource '{search_name}'")
    if result:
        # Get the endpoint and key
        endpoint_cmd = f"az search service show --name {search_name} --resource-group {resource_group_name} --query hostName -o tsv"
        key_cmd = f"az search admin-key show --name {search_name} --resource-group {resource_group_name} --query primaryKey -o tsv"
        
        endpoint = run_command(endpoint_cmd, "Getting Azure AI Search endpoint")
        api_key = run_command(key_cmd, "Getting Azure AI Search API key")
        
        if endpoint and api_key:
            return {
                'name': search_name,
                'endpoint': f"https://{endpoint}",
                'api_key': api_key
            }
    
    return None

def create_search_index(search_config):
    """Create the search index using Python script"""
    try:
        # Create a temporary Python script to create the index
        script_content = f'''
import os
import sys
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, VectorSearch,
    HnswAlgorithmConfiguration, VectorSearchProfile,
    SemanticSearch, SemanticConfiguration,
    SemanticPrioritizedFields, SemanticField
)
from azure.core.credentials import AzureKeyCredential

# Initialize search client
credential = AzureKeyCredential("{search_config['api_key']}")
index_client = SearchIndexClient(
    endpoint="{search_config['endpoint']}",
    credential=credential
)

# Define the index schema
index_name = "kt-ai-knowledge-base"
index = SearchIndex(
    name=index_name,
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
        SearchableField(
            name="content_vector",
            type="Collection(Edm.Single)",
            vector_search_dimensions=1536,
            vector_search_profile_name="default-vector-profile"
        )
    ],
    vector_search=VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="default-algorithm",
                parameters={{"m": 4, "efConstruction": 400, "efSearch": 500}}
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
                    content_fields=[SemanticField(field_name="content")]
                )
            )
        ]
    )
)

# Create the index
index_client.create_index(index)
print("Index created successfully!")
'''
        
        # Write and execute the script
        script_path = "/tmp/create_index.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        result = run_command(f"python {script_path}", "Creating search index")
        os.remove(script_path)
        
        return result is not None
        
    except Exception as e:
        logger.error(f"❌ Failed to create search index: {e}")
        return False

def generate_env_file(openai_config, search_config):
    """Generate .env file with credentials"""
    try:
        env_content = f"""# Database Configuration
DATABASE_URL=postgresql+asyncpg://kt_user:kt_password@localhost:5432/kt_ai

# Redis Configuration
REDIS_URL=redis://localhost:6379

# LLM API Keys (fallback)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Azure OpenAI
AZURE_OPENAI_ENDPOINT={openai_config['endpoint']}
AZURE_OPENAI_API_KEY={openai_config['api_key']}
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo

# Azure AI Search
AZURE_SEARCH_ENDPOINT={search_config['endpoint']}
AZURE_SEARCH_KEY={search_config['api_key']}
AZURE_SEARCH_INDEX_NAME=kt-ai-knowledge-base
AZURE_SEARCH_API_VERSION=2023-11-01

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# LLM Settings
DEFAULT_MODEL=gpt-4-turbo-preview
MAX_TOKENS=2000
TEMPERATURE=0.7

# Cache Settings
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
"""
        
        # Write to backend/.env
        env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        logger.info(f"✅ Generated .env file: {env_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to generate .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Simplified Azure Setup for Knowledge Transfer Bot")
    print("=" * 60)
    print("This script will create Azure AI Search and Azure OpenAI resources")
    print("using Azure CLI commands.")
    print()
    
    # Step 1: Check Azure CLI
    if not check_azure_cli():
        return False
    
    # Step 2: Login to Azure
    if not login_azure():
        return False
    
    # Step 3: Get subscription
    subscription = get_subscription()
    if not subscription:
        return False
    
    # Step 4: Get resource group name
    print("\n📁 Resource Group Configuration")
    print("-" * 40)
    resource_group_name = input("Enter resource group name (or press Enter for 'kt-ai-rg'): ").strip()
    if not resource_group_name:
        resource_group_name = "kt-ai-rg"
    
    # Step 5: Get location
    location = input("Enter Azure location (or press Enter for 'eastus'): ").strip()
    if not location:
        location = "eastus"
    
    # Step 6: Create resource group
    if not create_resource_group(resource_group_name, location):
        logger.error("❌ Failed to create resource group")
        return False
    
    # Step 7: Create Azure OpenAI
    logger.info("🧠 Creating Azure OpenAI resource...")
    openai_config = create_azure_openai(resource_group_name, location)
    if not openai_config:
        logger.error("❌ Failed to create Azure OpenAI")
        return False
    
    # Step 8: Create Azure AI Search
    logger.info("🔍 Creating Azure AI Search resource...")
    search_config = create_azure_search(resource_group_name, location)
    if not search_config:
        logger.error("❌ Failed to create Azure AI Search")
        return False
    
    # Step 9: Create search index
    logger.info("📊 Creating search index...")
    if not create_search_index(search_config):
        logger.error("❌ Failed to create search index")
        return False
    
    # Step 10: Generate .env file
    if not generate_env_file(openai_config, search_config):
        logger.error("❌ Failed to generate .env file")
        return False
    
    # Step 11: Print summary
    print("\n" + "=" * 60)
    print("🎉 Azure Setup Complete!")
    print("=" * 60)
    
    print(f"\n📁 Resource Group: {resource_group_name}")
    print(f"📍 Location: {location}")
    
    print(f"\n🧠 Azure OpenAI:")
    print(f"   Name: {openai_config['name']}")
    print(f"   Endpoint: {openai_config['endpoint']}")
    print(f"   API Key: {openai_config['api_key'][:8]}...")
    
    print(f"\n🔍 Azure AI Search:")
    print(f"   Name: {search_config['name']}")
    print(f"   Endpoint: {search_config['endpoint']}")
    print(f"   API Key: {search_config['api_key'][:8]}...")
    print(f"   Index: kt-ai-knowledge-base")
    
    print(f"\n📝 Next Steps:")
    print(f"1. Deploy models in Azure OpenAI Studio:")
    print(f"   https://oai.azure.com/")
    print(f"   Required models:")
    print(f"   - GPT-4 Turbo (deployment name: gpt-4-turbo)")
    print(f"   - GPT-3.5 Turbo (deployment name: gpt-3.5-turbo)")
    print(f"   - Text-Embedding-3-Large (deployment name: text-embedding-3-large)")
    print(f"2. Test the setup:")
    print(f"   python scripts/setup-azure-openai.py")
    print(f"   python scripts/setup-azure-search.py")
    print(f"3. Start the application:")
    print(f"   docker-compose up")
    
    print(f"\n🔐 Security Notes:")
    print(f"- Keep your API keys secure")
    print(f"- Consider using Azure Key Vault for production")
    print(f"- Enable private endpoints for production use")
    
    return True

if __name__ == "__main__":
    try:
        if main():
            print(f"\n🎉 Setup completed successfully!")
            print(f"Your Azure resources are ready for the Knowledge Transfer Bot.")
        else:
            print(f"\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)
