# Azure OpenAI Integration Guide

## 🧠 Azure OpenAI Integration for KT-AI

This guide explains how to integrate Azure OpenAI for LLM functionality in the Knowledge Transfer Bot, providing better performance, cost management, and Azure ecosystem integration.

## 🎯 Why Azure OpenAI?

### Benefits of Azure OpenAI

- **Enterprise Integration**: Seamless integration with Azure services
- **Cost Management**: Better cost control and monitoring
- **Security**: Enterprise-grade security and compliance
- **Performance**: Optimized for Azure infrastructure
- **Compliance**: SOC 2, ISO 27001, and other certifications
- **Data Residency**: Keep data within your Azure region

### Comparison with OpenAI API

| Feature | OpenAI API | Azure OpenAI |
|---------|------------|--------------|
| **Cost** | Pay-per-use | Enterprise pricing |
| **Security** | Standard | Enterprise-grade |
| **Compliance** | Limited | Full compliance |
| **Integration** | External | Native Azure |
| **Monitoring** | Basic | Advanced |
| **Data Residency** | Global | Regional control |

## 🚀 Setup Instructions

### 1. Create Azure OpenAI Resource

1. **Azure Portal Setup:**
   ```bash
   # Login to Azure
   az login
   
   # Create resource group
   az group create --name kt-ai-rg --location eastus
   
   # Create Azure OpenAI resource
   az cognitiveservices account create \
     --name kt-ai-openai \
     --resource-group kt-ai-rg \
     --location eastus \
     --kind OpenAI \
     --sku S0
   ```

2. **Get Service Credentials:**
   ```bash
   # Get the endpoint
   az cognitiveservices account show --name kt-ai-openai --resource-group kt-ai-rg --query "properties.endpoint"
   
   # Get the API key
   az cognitiveservices account keys list --name kt-ai-openai --resource-group kt-ai-rg --query "key1"
   ```

### 2. Deploy Models

1. **Access Azure OpenAI Studio:**
   - Go to https://oai.azure.com/
   - Select your resource
   - Navigate to "Deployments"

2. **Deploy Required Models:**
   - **GPT-4 Turbo**: For complex reasoning tasks
   - **GPT-3.5 Turbo**: For general tasks
   - **Text Embedding 3 Large**: For vector embeddings

3. **Note Deployment Names:**
   - Record the deployment names for configuration

### 3. Configure Environment Variables

Update your `backend/.env` file:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://kt-ai-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

### 4. Setup the Integration

Run the setup script to configure Azure OpenAI:

```bash
# Install Azure dependencies
cd backend
pip install azure-identity azure-mgmt-cognitiveservices

# Run the setup script
python ../scripts/setup-azure-openai.py
```

## 🔧 Code Changes

### 1. New Azure OpenAI Provider

**app/llm/providers/azure_openai_provider.py:**
- Complete Azure OpenAI implementation
- Text generation with streaming
- Embeddings generation
- Model management
- Error handling and retries

### 2. Updated LLM Orchestration

**app/llm/router.py:**
- Prioritizes Azure OpenAI for all tasks
- Fallback to OpenAI API if needed
- Cost optimization through model selection

### 3. Enhanced Vector Service

**app/services/azure_openai_embeddings.py:**
- Azure OpenAI embeddings service
- Batch embedding generation
- Embedding validation
- Performance optimization

### 4. Configuration Updates

**app/core/config.py:**
```python
# Azure OpenAI
azure_openai_endpoint: Optional[str] = None
azure_openai_api_key: Optional[str] = None
azure_openai_api_version: str = "2024-02-15-preview"
azure_openai_deployment_name: Optional[str] = None
```

## 📊 Model Configuration

### Task-Based Model Routing

| Task Type | Primary Model | Fallback Model | Use Case |
|-----------|---------------|----------------|----------|
| **Gap Analysis** | Azure OpenAI GPT-4 | OpenAI GPT-4 | Complex reasoning |
| **Question Generation** | Azure OpenAI GPT-4 | OpenAI GPT-4 | Creative tasks |
| **Classification** | Azure OpenAI GPT-3.5 | OpenAI GPT-3.5 | Fast processing |
| **Embeddings** | Azure OpenAI Text-Embedding-3-Large | OpenAI Text-Embedding-3-Large | Vector search |
| **Document Analysis** | Azure OpenAI GPT-4 | Anthropic Claude-3 | Long context |

### Model Capabilities

**GPT-4 Turbo (Azure OpenAI):**
- **Context**: 128k tokens
- **Use Cases**: Complex reasoning, gap analysis, question generation
- **Performance**: High accuracy, slower response

**GPT-3.5 Turbo (Azure OpenAI):**
- **Context**: 16k tokens
- **Use Cases**: Fast classification, simple tasks
- **Performance**: Fast response, good accuracy

**Text Embedding 3 Large (Azure OpenAI):**
- **Dimensions**: 3072
- **Use Cases**: Vector search, semantic similarity
- **Performance**: High quality embeddings

## 🔍 LLM Orchestration Features

### 1. Intelligent Model Selection

```python
# Automatic model selection based on task
response = await llm_orchestrator.generate(
    task_type="gap_analysis_deep",
    prompt="Analyze this ESG document for gaps",
    max_tokens=2000
)
```

### 2. Streaming Responses

```python
# Real-time streaming for long responses
async for chunk in llm_orchestrator.generate_stream(
    task_type="question_generation",
    prompt="Generate questions for ESG gap",
    max_tokens=1000
):
    print(chunk["content"])
```

### 3. Batch Processing

```python
# Process multiple requests in parallel
requests = [
    {"task_type": "gap_classification", "prompt": "Classify gap 1"},
    {"task_type": "gap_classification", "prompt": "Classify gap 2"},
    {"task_type": "gap_classification", "prompt": "Classify gap 3"}
]

results = await llm_orchestrator.batch_generate(requests)
```

### 4. Embeddings Generation

```python
# Generate embeddings for vector search
embeddings = await embeddings_service.generate_embeddings(
    texts=["ESG sustainability metrics", "Climate risk assessment"],
    model="text-embedding-3-large"
)
```

## 🚀 Performance Benefits

### 1. Cost Optimization
- **Enterprise Pricing**: Better rates for high-volume usage
- **Reserved Capacity**: Predictable costs with reserved instances
- **Token Optimization**: Smart model selection reduces costs

### 2. Performance Improvements
- **Azure Integration**: Faster response times within Azure
- **Caching**: Built-in response caching
- **Load Balancing**: Automatic load distribution

### 3. Enterprise Features
- **Security**: Enterprise-grade security controls
- **Compliance**: SOC 2, ISO 27001 compliance
- **Monitoring**: Advanced usage and performance monitoring

## 🔒 Security Features

### 1. Authentication
- **API Keys**: Secure API key management
- **Azure Identity**: Managed identity support
- **RBAC**: Role-based access control

### 2. Data Protection
- **Encryption**: Data encrypted in transit and at rest
- **Network Security**: VNet integration support
- **Access Control**: IP restrictions and private endpoints

### 3. Compliance
- **Data Residency**: Keep data within your region
- **Audit Logging**: Comprehensive audit trails
- **Privacy**: GDPR and privacy compliance

## 📈 Monitoring and Analytics

### 1. Usage Metrics
- **Token Usage**: Track token consumption by model
- **Request Volume**: Monitor API request patterns
- **Cost Tracking**: Real-time cost monitoring

### 2. Performance Metrics
- **Response Time**: Track model response times
- **Error Rates**: Monitor failed requests
- **Throughput**: Measure requests per second

### 3. Quality Metrics
- **Accuracy**: Track model accuracy for different tasks
- **Relevance**: Measure response relevance
- **User Satisfaction**: Monitor user feedback

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Check credentials
   az cognitiveservices account show --name kt-ai-openai --resource-group kt-ai-rg
   ```

2. **Model Deployment Issues**
   ```bash
   # Check deployment status
   az cognitiveservices account show --name kt-ai-openai --resource-group kt-ai-rg --query "properties.endpoint"
   ```

3. **Rate Limiting**
   - Check Azure OpenAI quotas
   - Implement exponential backoff
   - Use multiple deployments

### Debug Commands

```bash
# Test Azure OpenAI connection
python scripts/setup-azure-openai.py

# Check model availability
curl -H "api-key: YOUR_KEY" "https://kt-ai-openai.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT/chat/completions?api-version=2024-02-15-preview" -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## 📚 Additional Resources

### Documentation
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/ai-services/openai/)
- [Model Deployment Guide](https://docs.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource)
- [Best Practices](https://docs.microsoft.com/en-us/azure/ai-services/openai/concepts/overview)

### Best Practices
- [Performance Optimization](https://docs.microsoft.com/en-us/azure/ai-services/openai/how-to/optimize-performance)
- [Security Best Practices](https://docs.microsoft.com/en-us/azure/ai-services/openai/concepts/security)
- [Cost Management](https://docs.microsoft.com/en-us/azure/ai-services/openai/how-to/manage-costs)

## 🎉 Integration Complete

After following this guide, your Knowledge Transfer Bot will be using Azure OpenAI for:

- ✅ **LLM Generation**: GPT-4 and GPT-3.5 for all tasks
- ✅ **Embeddings**: Text-Embedding-3-Large for vector search
- ✅ **Streaming**: Real-time response streaming
- ✅ **Batch Processing**: Parallel request processing
- ✅ **Enterprise Features**: Security, compliance, and monitoring

The integration maintains the same API interface while providing enterprise-grade LLM capabilities with better performance, security, and cost management.
