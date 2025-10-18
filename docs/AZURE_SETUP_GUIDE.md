# Azure Setup Guide for Knowledge Transfer Bot

## 🚀 Complete Azure Infrastructure Setup

This guide provides step-by-step instructions for setting up Azure AI Search and Azure OpenAI resources for the Knowledge Transfer Bot.

## 📋 Prerequisites

### Required Tools
- **Azure CLI**: [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Python 3.8+**: For running setup scripts
- **Azure Subscription**: Active Azure subscription with appropriate permissions

### Required Permissions
- **Contributor** role on the target resource group
- **Cognitive Services Contributor** role for Azure OpenAI
- **Search Service Contributor** role for Azure AI Search

## 🛠️ Setup Options

### Option 1: Automated Setup (Recommended)

#### Simple Setup (Azure CLI)
```bash
# Install dependencies
pip install -r scripts/requirements-azure.txt

# Run the simplified setup script
python scripts/azure-setup-simple.py
```

#### Advanced Setup (Python SDK)
```bash
# Install dependencies
pip install -r scripts/requirements-azure.txt

# Run the advanced setup script
python scripts/azure-setup.py
```

### Option 2: Manual Setup

#### Step 1: Login to Azure
```bash
az login
```

#### Step 2: Create Resource Group
```bash
# Set variables
RESOURCE_GROUP="kt-ai-rg"
LOCATION="eastus"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION
```

#### Step 3: Create Azure OpenAI
```bash
# Set variables
OPENAI_NAME="kt-ai-openai-$(date +%s)"

# Create Azure OpenAI resource
az cognitiveservices account create \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --kind OpenAI \
    --sku S0

# Get endpoint and key
OPENAI_ENDPOINT=$(az cognitiveservices account show --name $OPENAI_NAME --resource-group $RESOURCE_GROUP --query properties.endpoint -o tsv)
OPENAI_KEY=$(az cognitiveservices account keys list --name $OPENAI_NAME --resource-group $RESOURCE_GROUP --query key1 -o tsv)
```

#### Step 4: Create Azure AI Search
```bash
# Set variables
SEARCH_NAME="kt-ai-search-$(date +%s)"

# Create Azure AI Search resource
az search service create \
    --name $SEARCH_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku standard \
    --partition-count 1 \
    --replica-count 1

# Get endpoint and key
SEARCH_ENDPOINT=$(az search service show --name $SEARCH_NAME --resource-group $RESOURCE_GROUP --query hostName -o tsv)
SEARCH_KEY=$(az search admin-key show --name $SEARCH_NAME --resource-group $RESOURCE_GROUP --query primaryKey -o tsv)
```

#### Step 5: Create Search Index
```bash
# Create the search index
python scripts/setup-azure-search.py
```

## 🔧 Configuration

### Environment Variables

After running the setup, update your `backend/.env` file:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your_search_key_here
AZURE_SEARCH_INDEX_NAME=kt-ai-knowledge-base
AZURE_SEARCH_API_VERSION=2023-11-01
```

### Model Deployment

1. **Access Azure OpenAI Studio**
   - Go to [https://oai.azure.com/](https://oai.azure.com/)
   - Select your Azure OpenAI resource

2. **Deploy Required Models**
   - **GPT-4 Turbo**: For complex reasoning tasks
     - Deployment name: `gpt-4-turbo`
     - Model: `gpt-4-turbo-preview`
   - **GPT-3.5 Turbo**: For general tasks
     - Deployment name: `gpt-3.5-turbo`
     - Model: `gpt-3.5-turbo`
   - **Text Embedding 3 Large**: For vector search
     - Deployment name: `text-embedding-3-large`
     - Model: `text-embedding-3-large`

## 🧪 Testing the Setup

### Test Azure OpenAI
```bash
python scripts/setup-azure-openai.py
```

### Test Azure AI Search
```bash
python scripts/setup-azure-search.py
```

### Test Full Application
```bash
# Start the application
docker-compose up

# Test the API
curl http://localhost:8001/health
```

## 📊 Resource Configuration

### Azure OpenAI Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| **SKU** | S0 | Standard tier |
| **Region** | East US | Primary region |
| **Models** | GPT-4, GPT-3.5, Embeddings | Required models |

### Azure AI Search Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| **SKU** | Standard | Standard tier |
| **Partitions** | 1 | Storage partitions |
| **Replicas** | 1 | Search replicas |
| **Index** | kt-ai-knowledge-base | Vector search index |

### Search Index Schema

```json
{
  "name": "kt-ai-knowledge-base",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true
    },
    {
      "name": "content_vector",
      "type": "Collection(Edm.Single)",
      "vectorSearchDimensions": 1536
    }
  ],
  "vectorSearch": {
    "algorithms": ["hnsw"],
    "profiles": ["default-vector-profile"]
  },
  "semanticSearch": {
    "configurations": ["default-semantic-config"]
  }
}
```

## 💰 Cost Estimation

### Azure OpenAI Costs (Monthly)

| Model | Usage | Cost |
|-------|-------|------|
| **GPT-4 Turbo** | 1M tokens | ~$30 |
| **GPT-3.5 Turbo** | 10M tokens | ~$20 |
| **Text Embedding 3 Large** | 1M tokens | ~$0.13 |

### Azure AI Search Costs (Monthly)

| Component | Cost |
|-----------|------|
| **Standard Tier** | $250 |
| **Storage** | $0.25/GB |
| **Queries** | $0.50/1000 queries |

### Total Estimated Cost
- **Development**: ~$300-500/month
- **Production**: ~$500-1000/month

## 🔒 Security Configuration

### Network Security
```bash
# Enable private endpoints
az network private-endpoint create \
    --name openai-pe \
    --resource-group $RESOURCE_GROUP \
    --vnet-name $VNET_NAME \
    --subnet $SUBNET_NAME \
    --private-connection-resource-id $OPENAI_RESOURCE_ID
```

### Access Control
```bash
# Create managed identity
az identity create --name kt-ai-identity --resource-group $RESOURCE_GROUP

# Assign roles
az role assignment create \
    --assignee $IDENTITY_PRINCIPAL_ID \
    --role "Cognitive Services User" \
    --scope $OPENAI_RESOURCE_ID
```

### Key Management
```bash
# Use Azure Key Vault
az keyvault create --name kt-ai-vault --resource-group $RESOURCE_GROUP

# Store secrets
az keyvault secret set --vault-name kt-ai-vault --name openai-key --value $OPENAI_KEY
az keyvault secret set --vault-name kt-ai-vault --name search-key --value $SEARCH_KEY
```

## 📈 Monitoring and Analytics

### Azure Monitor
```bash
# Enable diagnostic settings
az monitor diagnostic-settings create \
    --name kt-ai-diagnostics \
    --resource $OPENAI_RESOURCE_ID \
    --logs '[{"category": "AuditLogs", "enabled": true}]'
```

### Cost Management
```bash
# Set up budget alerts
az consumption budget create \
    --budget-name kt-ai-budget \
    --amount 500 \
    --resource-group $RESOURCE_GROUP
```

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Re-login to Azure
   az login
   
   # Check subscription
   az account show
   ```

2. **Permission Errors**
   ```bash
   # Check permissions
   az role assignment list --assignee $USER_ID
   
   # Add required roles
   az role assignment create --assignee $USER_ID --role "Contributor"
   ```

3. **Resource Creation Failures**
   ```bash
   # Check resource availability
   az cognitiveservices account list-skus --kind OpenAI --location $LOCATION
   ```

4. **Model Deployment Issues**
   - Check model availability in your region
   - Verify deployment quotas
   - Wait for model to be fully deployed

### Debug Commands

```bash
# Check resource status
az cognitiveservices account show --name $OPENAI_NAME --resource-group $RESOURCE_GROUP

# Test Azure OpenAI
curl -H "api-key: $OPENAI_KEY" \
     -H "Content-Type: application/json" \
     "$OPENAI_ENDPOINT/openai/deployments/gpt-4-turbo/chat/completions?api-version=2024-02-15-preview" \
     -d '{"messages": [{"role": "user", "content": "Hello"}]}'

# Test Azure AI Search
curl -H "api-key: $SEARCH_KEY" \
     "$SEARCH_ENDPOINT/indexes/kt-ai-knowledge-base/docs/search?api-version=2023-11-01" \
     -d '{"search": "test"}'
```

## 📚 Additional Resources

### Documentation
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure AI Search Documentation](https://docs.microsoft.com/en-us/azure/search/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)

### Best Practices
- [Azure OpenAI Best Practices](https://docs.microsoft.com/en-us/azure/ai-services/openai/concepts/overview)
- [Azure AI Search Best Practices](https://docs.microsoft.com/en-us/azure/search/search-performance-optimization)
- [Cost Optimization](https://docs.microsoft.com/en-us/azure/ai-services/openai/how-to/manage-costs)

### Support
- [Azure Support](https://azure.microsoft.com/en-us/support/)
- [Azure OpenAI Community](https://techcommunity.microsoft.com/t5/azure-ai-services/bd-p/AzureAIServices)
- [GitHub Issues](https://github.com/your-repo/issues)

## 🎉 Next Steps

After completing the Azure setup:

1. **Deploy Models**: Deploy required models in Azure OpenAI Studio
2. **Test Integration**: Run the test scripts to verify functionality
3. **Start Application**: Launch the Knowledge Transfer Bot
4. **Monitor Usage**: Set up monitoring and cost alerts
5. **Scale Resources**: Adjust resources based on usage patterns

Your Azure infrastructure is now ready for the Knowledge Transfer Bot! 🚀
