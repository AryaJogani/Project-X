#!/usr/bin/env python3
"""
Azure Setup Script for KT-AI
Creates Azure AI Search and Azure OpenAI resources with required configurations
"""

import os
import sys
import json
import time
import asyncio
import logging
from typing import Dict, Any, Optional
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.search import SearchManagementClient
from azure.mgmt.cognitiveservices.models import (
    CognitiveServicesAccount,
    Sku,
    ApiProperties
)
from azure.mgmt.search.models import (
    SearchService,
    Sku as SearchSku,
    SearchServiceProperties
)
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

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AzureSetupManager:
    """Manages Azure resource creation and configuration"""
    
    def __init__(self):
        self.credential = None
        self.subscription_id = None
        self.resource_group_name = None
        self.location = "East US"
        self.results = {}
    
    async def authenticate(self):
        """Authenticate with Azure"""
        try:
            logger.info("🔐 Authenticating with Azure...")
            
            # Try different authentication methods
            try:
                self.credential = DefaultAzureCredential()
                logger.info("✓ Using DefaultAzureCredential")
            except Exception:
                self.credential = InteractiveBrowserCredential()
                logger.info("✓ Using InteractiveBrowserCredential")
            
            # Get subscription ID
            from azure.mgmt.resource import SubscriptionClient
            subscription_client = SubscriptionClient(self.credential)
            subscriptions = list(subscription_client.subscriptions.list())
            
            if not subscriptions:
                raise Exception("No Azure subscriptions found")
            
            if len(subscriptions) == 1:
                self.subscription_id = subscriptions[0].subscription_id
                logger.info(f"✓ Using subscription: {subscriptions[0].display_name}")
            else:
                print("\n📋 Available subscriptions:")
                for i, sub in enumerate(subscriptions):
                    print(f"{i+1}. {sub.display_name} ({sub.subscription_id})")
                
                while True:
                    try:
                        choice = int(input(f"\nSelect subscription (1-{len(subscriptions)}): ")) - 1
                        if 0 <= choice < len(subscriptions):
                            self.subscription_id = subscriptions[choice].subscription_id
                            logger.info(f"✓ Selected subscription: {subscriptions[choice].display_name}")
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False
    
    async def get_resource_group_name(self):
        """Get resource group name from user"""
        print("\n📁 Resource Group Configuration")
        print("=" * 50)
        
        # Check if resource group exists
        resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        
        while True:
            self.resource_group_name = input("Enter resource group name (or press Enter for 'kt-ai-rg'): ").strip()
            if not self.resource_group_name:
                self.resource_group_name = "kt-ai-rg"
            
            try:
                # Check if resource group exists
                rg = resource_client.resource_groups.get(self.resource_group_name)
                logger.info(f"✓ Resource group '{self.resource_group_name}' already exists")
                break
            except Exception:
                # Resource group doesn't exist, create it
                create = input(f"Resource group '{self.resource_group_name}' doesn't exist. Create it? (y/n): ").lower()
                if create == 'y':
                    try:
                        resource_client.resource_groups.create_or_update(
                            self.resource_group_name,
                            {"location": self.location}
                        )
                        logger.info(f"✓ Created resource group: {self.resource_group_name}")
                        break
                    except Exception as e:
                        logger.error(f"❌ Failed to create resource group: {e}")
                        continue
                else:
                    continue
    
    async def create_azure_openai(self):
        """Create Azure OpenAI resource"""
        try:
            logger.info("🧠 Creating Azure OpenAI resource...")
            
            # Generate unique names
            openai_name = f"kt-ai-openai-{int(time.time())}"
            
            # Create Azure OpenAI resource
            cognitiveservices_client = CognitiveServicesManagementClient(
                self.credential, self.subscription_id
            )
            
            # Create the resource
            openai_resource = CognitiveServicesAccount(
                location=self.location,
                kind="OpenAI",
                sku=Sku(name="S0", tier="Standard"),
                properties=ApiProperties(
                    custom_sub_domain_name=openai_name
                )
            )
            
            logger.info(f"Creating Azure OpenAI resource: {openai_name}")
            operation = cognitiveservices_client.accounts.begin_create(
                self.resource_group_name,
                openai_name,
                openai_resource
            )
            
            # Wait for completion
            while not operation.done():
                logger.info("⏳ Creating Azure OpenAI resource...")
                await asyncio.sleep(10)
            
            openai_account = operation.result()
            
            # Get the endpoint and keys
            keys = cognitiveservices_client.accounts.list_keys(
                self.resource_group_name, openai_name
            )
            
            endpoint = f"https://{openai_name}.openai.azure.com/"
            api_key = keys.key1
            
            self.results['azure_openai'] = {
                'name': openai_name,
                'endpoint': endpoint,
                'api_key': api_key,
                'resource_group': self.resource_group_name
            }
            
            logger.info(f"✅ Azure OpenAI created successfully!")
            logger.info(f"   Name: {openai_name}")
            logger.info(f"   Endpoint: {endpoint}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create Azure OpenAI: {e}")
            return False
    
    async def create_azure_search(self):
        """Create Azure AI Search resource"""
        try:
            logger.info("🔍 Creating Azure AI Search resource...")
            
            # Generate unique names
            search_name = f"kt-ai-search-{int(time.time())}"
            
            # Create Azure AI Search resource
            search_client = SearchManagementClient(
                self.credential, self.subscription_id
            )
            
            # Create the search service
            search_service = SearchService(
                location=self.location,
                sku=SearchSku(name="standard"),
                replica_count=1,
                partition_count=1,
                hosting_mode="default"
            )
            
            logger.info(f"Creating Azure AI Search resource: {search_name}")
            operation = search_client.services.begin_create_or_update(
                self.resource_group_name,
                search_name,
                search_service
            )
            
            # Wait for completion
            while not operation.done():
                logger.info("⏳ Creating Azure AI Search resource...")
                await asyncio.sleep(10)
            
            search_account = operation.result()
            
            # Get the admin keys
            admin_keys = search_client.admin_keys.get(
                self.resource_group_name, search_name
            )
            
            endpoint = f"https://{search_name}.search.windows.net"
            api_key = admin_keys.primary_key
            
            self.results['azure_search'] = {
                'name': search_name,
                'endpoint': endpoint,
                'api_key': api_key,
                'resource_group': self.resource_group_name
            }
            
            logger.info(f"✅ Azure AI Search created successfully!")
            logger.info(f"   Name: {search_name}")
            logger.info(f"   Endpoint: {endpoint}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create Azure AI Search: {e}")
            return False
    
    async def create_search_index(self):
        """Create the search index"""
        try:
            logger.info("📊 Creating search index...")
            
            search_config = self.results['azure_search']
            endpoint = search_config['endpoint']
            api_key = search_config['api_key']
            
            # Initialize search client
            credential = AzureKeyCredential(api_key)
            index_client = SearchIndexClient(
                endpoint=endpoint,
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
            logger.info(f"✅ Search index '{index_name}' created successfully!")
            
            self.results['search_index'] = {
                'name': index_name,
                'endpoint': endpoint,
                'api_key': api_key
            }
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create search index: {e}")
            return False
    
    async def deploy_openai_models(self):
        """Deploy OpenAI models"""
        try:
            logger.info("🤖 Deploying OpenAI models...")
            logger.info("⚠️  Note: Model deployment must be done manually in Azure OpenAI Studio")
            logger.info("   Please visit: https://oai.azure.com/")
            logger.info("   Required models to deploy:")
            logger.info("   1. GPT-4 Turbo (for complex tasks)")
            logger.info("   2. GPT-3.5 Turbo (for general tasks)")
            logger.info("   3. Text-Embedding-3-Large (for embeddings)")
            
            # Store deployment instructions
            self.results['model_deployment'] = {
                'instructions': [
                    "Visit https://oai.azure.com/",
                    "Select your Azure OpenAI resource",
                    "Go to 'Deployments' section",
                    "Deploy the following models:",
                    "  - GPT-4 Turbo (deployment name: gpt-4-turbo)",
                    "  - GPT-3.5 Turbo (deployment name: gpt-3.5-turbo)",
                    "  - Text-Embedding-3-Large (deployment name: text-embedding-3-large)"
                ]
            }
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model deployment instructions failed: {e}")
            return False
    
    async def generate_env_file(self):
        """Generate .env file with credentials"""
        try:
            logger.info("📝 Generating .env file...")
            
            env_content = f"""# Database Configuration
DATABASE_URL=postgresql+asyncpg://kt_user:kt_password@localhost:5432/kt_ai

# Redis Configuration
REDIS_URL=redis://localhost:6379

# LLM API Keys (fallback)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Azure OpenAI
AZURE_OPENAI_ENDPOINT={self.results['azure_openai']['endpoint']}
AZURE_OPENAI_API_KEY={self.results['azure_openai']['api_key']}
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo

# Azure AI Search
AZURE_SEARCH_ENDPOINT={self.results['azure_search']['endpoint']}
AZURE_SEARCH_KEY={self.results['azure_search']['api_key']}
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
    
    async def save_results(self):
        """Save setup results to file"""
        try:
            results_path = os.path.join(os.path.dirname(__file__), 'azure-setup-results.json')
            with open(results_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            logger.info(f"✅ Setup results saved to: {results_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
            return False
    
    async def print_summary(self):
        """Print setup summary"""
        print("\n" + "=" * 60)
        print("🎉 Azure Setup Complete!")
        print("=" * 60)
        
        print(f"\n📁 Resource Group: {self.resource_group_name}")
        print(f"📍 Location: {self.location}")
        
        print(f"\n🧠 Azure OpenAI:")
        print(f"   Name: {self.results['azure_openai']['name']}")
        print(f"   Endpoint: {self.results['azure_openai']['endpoint']}")
        print(f"   API Key: {self.results['azure_openai']['api_key'][:8]}...")
        
        print(f"\n🔍 Azure AI Search:")
        print(f"   Name: {self.results['azure_search']['name']}")
        print(f"   Endpoint: {self.results['azure_search']['endpoint']}")
        print(f"   API Key: {self.results['azure_search']['api_key'][:8]}...")
        print(f"   Index: kt-ai-knowledge-base")
        
        print(f"\n📝 Next Steps:")
        print(f"1. Deploy models in Azure OpenAI Studio:")
        print(f"   https://oai.azure.com/")
        print(f"2. Test the setup:")
        print(f"   python scripts/setup-azure-openai.py")
        print(f"   python scripts/setup-azure-search.py")
        print(f"3. Start the application:")
        print(f"   docker-compose up")
        
        print(f"\n🔐 Security Notes:")
        print(f"- Keep your API keys secure")
        print(f"- Consider using Azure Key Vault for production")
        print(f"- Enable private endpoints for production use")

async def main():
    """Main setup function"""
    print("🚀 Azure Setup for Knowledge Transfer Bot")
    print("=" * 50)
    print("This script will create Azure AI Search and Azure OpenAI resources")
    print("with the required configurations for the KT-AI application.")
    print()
    
    setup_manager = AzureSetupManager()
    
    # Step 1: Authenticate
    if not await setup_manager.authenticate():
        logger.error("❌ Authentication failed. Exiting.")
        sys.exit(1)
    
    # Step 2: Get resource group
    await setup_manager.get_resource_group_name()
    
    # Step 3: Create Azure OpenAI
    if not await setup_manager.create_azure_openai():
        logger.error("❌ Azure OpenAI creation failed. Exiting.")
        sys.exit(1)
    
    # Step 4: Create Azure AI Search
    if not await setup_manager.create_azure_search():
        logger.error("❌ Azure AI Search creation failed. Exiting.")
        sys.exit(1)
    
    # Step 5: Create search index
    if not await setup_manager.create_search_index():
        logger.error("❌ Search index creation failed. Exiting.")
        sys.exit(1)
    
    # Step 6: Deploy models (instructions)
    await setup_manager.deploy_openai_models()
    
    # Step 7: Generate .env file
    if not await setup_manager.generate_env_file():
        logger.error("❌ Failed to generate .env file.")
        sys.exit(1)
    
    # Step 8: Save results
    await setup_manager.save_results()
    
    # Step 9: Print summary
    await setup_manager.print_summary()
    
    print(f"\n🎉 Setup completed successfully!")
    print(f"Your Azure resources are ready for the Knowledge Transfer Bot.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)
