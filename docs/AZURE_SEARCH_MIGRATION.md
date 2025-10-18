# Azure AI Search Migration Guide

## 🔄 Migration from ChromaDB to Azure AI Search

This guide explains how to migrate from ChromaDB to Azure AI Search for the Knowledge Transfer Bot's vector database functionality.

## 🎯 Why Azure AI Search?

### Benefits of Azure AI Search

- **Enterprise-Grade**: Production-ready cloud service with high availability
- **Scalability**: Automatically scales with your data and query volume
- **Advanced Features**: Semantic search, hybrid search, and AI-powered ranking
- **Integration**: Native integration with Azure services and OpenAI
- **Performance**: Optimized for large-scale vector and text search
- **Security**: Enterprise security features and compliance certifications

### Comparison with ChromaDB

| Feature | ChromaDB | Azure AI Search |
|---------|----------|-----------------|
| **Deployment** | Self-hosted | Cloud service |
| **Scalability** | Manual scaling | Auto-scaling |
| **Semantic Search** | Basic | Advanced with AI |
| **Hybrid Search** | Limited | Full support |
| **Security** | Basic | Enterprise-grade |
| **Maintenance** | Manual | Managed service |

## 🚀 Setup Instructions

### 1. Create Azure AI Search Service

1. **Azure Portal Setup:**
   ```bash
   # Login to Azure
   az login
   
   # Create resource group
   az group create --name kt-ai-rg --location eastus
   
   # Create Azure AI Search service
   az search service create \
     --name kt-ai-search \
     --resource-group kt-ai-rg \
     --location eastus \
     --sku Standard
   ```

2. **Get Service Credentials:**
   ```bash
   # Get the endpoint
   az search service show --name kt-ai-search --resource-group kt-ai-rg --query "hostName"
   
   # Get the admin key
   az search admin-key show --name kt-ai-search --resource-group kt-ai-rg --query "primaryKey"
   ```

### 2. Configure Environment Variables

Update your `backend/.env` file:

```bash
# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://kt-ai-search.search.windows.net
AZURE_SEARCH_KEY=your_admin_key_here
AZURE_SEARCH_INDEX_NAME=kt-ai-knowledge-base
AZURE_SEARCH_API_VERSION=2023-11-01
```

### 3. Setup the Search Index

Run the setup script to create the Azure AI Search index:

```bash
# Install Azure dependencies
cd backend
pip install azure-search-documents azure-identity

# Run the setup script
python ../scripts/setup-azure-search.py
```

### 4. Update Docker Compose

The Docker Compose configuration has been updated to remove ChromaDB and include Azure AI Search environment variables:

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - AZURE_SEARCH_ENDPOINT=${AZURE_SEARCH_ENDPOINT}
      - AZURE_SEARCH_KEY=${AZURE_SEARCH_KEY}
      - AZURE_SEARCH_INDEX_NAME=kt-ai-knowledge-base
```

## 🔧 Code Changes

### 1. Updated Dependencies

**requirements.txt:**
```python
# Vector Database - Azure AI Search
azure-search-documents==11.4.0
azure-identity==1.15.0
azure-core==1.29.5
sentence-transformers==2.3.1
```

### 2. New Azure AI Search Service

**app/services/azure_search_service.py:**
- Complete Azure AI Search implementation
- Vector search with embeddings
- Semantic search capabilities
- Hybrid search support
- Index management

### 3. Updated Vector Service

**app/services/vector_service.py:**
- Wrapper around Azure AI Search service
- Maintains same API interface
- Enhanced with Azure AI Search features

### 4. Configuration Updates

**app/core/config.py:**
```python
# Azure AI Search
azure_search_endpoint: str = "https://your-search-service.search.windows.net"
azure_search_key: Optional[str] = None
azure_search_index_name: str = "kt-ai-knowledge-base"
azure_search_api_version: str = "2023-11-01"
```

## 📊 Index Schema

The Azure AI Search index includes:

### Fields
- **id**: Unique identifier (key field)
- **document_id**: Document identifier
- **content**: Searchable text content
- **title**: Document title
- **path**: File path
- **file_type**: Document type
- **chunk_index**: Chunk position
- **created_at/updated_at**: Timestamps
- **content_vector**: Vector embeddings (1536 dimensions)

### Vector Search Configuration
- **Algorithm**: HNSW (Hierarchical Navigable Small World)
- **Dimensions**: 1536 (OpenAI embeddings)
- **Parameters**: Optimized for performance

### Semantic Search Configuration
- **Title Field**: Document titles
- **Content Fields**: Main content for semantic understanding

## 🔍 Search Capabilities

### 1. Text Search
```python
# Basic text search
results = await vector_service.search(
    query="ESG sustainability metrics",
    n_results=5
)
```

### 2. Vector Search
```python
# Vector search with embeddings
results = await vector_service.search_with_embeddings(
    query_embedding=embedding_vector,
    n_results=5
)
```

### 3. Hybrid Search
```python
# Combines text and vector search
results = await vector_service.search(
    query="climate risk assessment",
    n_results=5,
    vector_query=vector_query
)
```

### 4. Filtered Search
```python
# Search with metadata filters
results = await vector_service.search(
    query="governance policies",
    n_results=5,
    filter_metadata={"file_type": "pdf", "document_id": "doc123"}
)
```

## 🚀 Performance Benefits

### 1. Scalability
- **Auto-scaling**: Automatically handles increased load
- **Partitioning**: Data distributed across multiple partitions
- **Replicas**: Multiple replicas for high availability

### 2. Search Performance
- **HNSW Algorithm**: Optimized vector search
- **Caching**: Built-in query result caching
- **Indexing**: Optimized for fast retrieval

### 3. Advanced Features
- **Semantic Search**: AI-powered understanding
- **Hybrid Search**: Combines text and vector search
- **Relevance Scoring**: Advanced ranking algorithms

## 🔒 Security Features

### 1. Authentication
- **API Keys**: Primary authentication method
- **Azure Identity**: Managed identity support
- **RBAC**: Role-based access control

### 2. Data Protection
- **Encryption**: Data encrypted at rest and in transit
- **Network Security**: VNet integration support
- **Access Control**: IP restrictions and private endpoints

### 3. Compliance
- **SOC 2**: Security and availability controls
- **ISO 27001**: Information security management
- **GDPR**: Data protection compliance

## 📈 Monitoring and Analytics

### 1. Search Analytics
- **Query Performance**: Search latency and throughput
- **Usage Metrics**: Query patterns and volume
- **Error Rates**: Failed queries and errors

### 2. Index Statistics
- **Document Count**: Total indexed documents
- **Storage Size**: Index storage usage
- **Index Health**: Index status and performance

### 3. Cost Management
- **Query Volume**: Track search operations
- **Storage Usage**: Monitor index size
- **Performance Tiers**: Optimize for cost vs performance

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Check credentials
   az search service show --name kt-ai-search --resource-group kt-ai-rg
   ```

2. **Index Creation Failures**
   ```bash
   # Check service status
   az search service show --name kt-ai-search --resource-group kt-ai-rg --query "status"
   ```

3. **Search Performance Issues**
   - Check index configuration
   - Verify vector dimensions
   - Monitor query patterns

### Debug Commands

```bash
# Check service health
curl -H "api-key: YOUR_KEY" "https://kt-ai-search.search.windows.net/indexes/kt-ai-knowledge-base/stats?api-version=2023-11-01"

# Test search
curl -H "api-key: YOUR_KEY" "https://kt-ai-search.search.windows.net/indexes/kt-ai-knowledge-base/docs/search?api-version=2023-11-01" -d '{"search": "test"}'
```

## 📚 Additional Resources

### Documentation
- [Azure AI Search Documentation](https://docs.microsoft.com/en-us/azure/search/)
- [Vector Search Guide](https://docs.microsoft.com/en-us/azure/search/vector-search-overview)
- [Semantic Search](https://docs.microsoft.com/en-us/azure/search/semantic-search-overview)

### Best Practices
- [Performance Optimization](https://docs.microsoft.com/en-us/azure/search/search-performance-optimization)
- [Security Best Practices](https://docs.microsoft.com/en-us/azure/search/search-security-overview)
- [Cost Optimization](https://docs.microsoft.com/en-us/azure/search/search-sku-tier)

## 🎉 Migration Complete

After following this guide, your Knowledge Transfer Bot will be using Azure AI Search for:

- ✅ **Vector Search**: High-performance semantic search
- ✅ **Text Search**: Full-text search capabilities
- ✅ **Hybrid Search**: Combined text and vector search
- ✅ **Semantic Search**: AI-powered understanding
- ✅ **Enterprise Features**: Security, scalability, and monitoring

The migration maintains the same API interface while providing enterprise-grade search capabilities.
