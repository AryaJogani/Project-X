"""
Azure AI Search service for vector search and document indexing
"""

from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime

from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

from app.core.config import settings

logger = logging.getLogger(__name__)

class AzureSearchService:
    """
    Azure AI Search service for vector search and document indexing
    """
    
    def __init__(self):
        self.search_client = None
        self.index_client = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Azure AI Search clients"""
        if self.initialized:
            return
            
        try:
            # Initialize credentials
            if settings.azure_search_key:
                credential = AzureKeyCredential(settings.azure_search_key)
            else:
                # Use Azure Identity for authentication
                credential = DefaultAzureCredential()
            
            # Initialize search clients
            self.search_client = SearchClient(
                endpoint=settings.azure_search_endpoint,
                index_name=settings.azure_search_index_name,
                credential=credential
            )
            
            self.index_client = SearchIndexClient(
                endpoint=settings.azure_search_endpoint,
                credential=credential
            )
            
            # Create index if it doesn't exist
            await self._ensure_index_exists()
            
            self.initialized = True
            logger.info("✓ Azure AI Search service initialized")
            
        except Exception as e:
            logger.error(f"❌ Azure AI Search initialization failed: {e}")
            raise
    
    async def _ensure_index_exists(self):
        """Create the search index if it doesn't exist"""
        try:
            # Check if index exists
            index_names = [index.name for index in self.index_client.list_indexes()]
            
            if settings.azure_search_index_name not in index_names:
                # Create the index
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
                self.index_client.create_index(index)
                logger.info(f"✓ Created Azure AI Search index: {settings.azure_search_index_name}")
            else:
                logger.info(f"✓ Azure AI Search index already exists: {settings.azure_search_index_name}")
                
        except Exception as e:
            logger.error(f"Failed to create Azure AI Search index: {e}")
            raise
    
    async def index_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any],
        embeddings: Optional[List[List[float]]] = None
    ):
        """
        Index document chunks in Azure AI Search
        
        Args:
            document_id: Document identifier
            content: Document content
            metadata: Document metadata
            embeddings: Optional pre-computed embeddings
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Split into chunks
            chunks = self._chunk_document(content, chunk_size=500)
            
            # Prepare documents for indexing
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    "id": f"{document_id}_chunk_{i}",
                    "document_id": document_id,
                    "content": chunk,
                    "title": metadata.get("title", ""),
                    "path": metadata.get("path", ""),
                    "file_type": metadata.get("file_type", "markdown"),
                    "chunk_index": i,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Add embeddings if provided
                if embeddings and i < len(embeddings):
                    doc["content_vector"] = embeddings[i]
                
                documents.append(doc)
            
            # Index documents
            result = self.search_client.upload_documents(documents)
            
            logger.info(f"Indexed {len(documents)} chunks for document: {document_id}")
            return result
            
        except Exception as e:
            logger.error(f"Document indexing error: {e}")
            raise
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None,
        vector_query: Optional[VectorizedQuery] = None
    ) -> Dict[str, Any]:
        """
        Semantic search across knowledge base
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            vector_query: Optional vector query for hybrid search
            
        Returns:
            Search results
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Build filter expression
            filter_expr = None
            if filter_metadata:
                filter_parts = []
                for key, value in filter_metadata.items():
                    if isinstance(value, str):
                        filter_parts.append(f"{key} eq '{value}'")
                    else:
                        filter_parts.append(f"{key} eq {value}")
                filter_expr = " and ".join(filter_parts)
            
            # Prepare search parameters
            search_params = {
                "search_text": query,
                "top": n_results,
                "include_total_count": True
            }
            
            if filter_expr:
                search_params["filter"] = filter_expr
            
            # Add vector search if provided
            if vector_query:
                search_params["vector_queries"] = [vector_query]
                search_params["vector_search_profile"] = "default-vector-profile"
            
            # Perform search
            results = self.search_client.search(**search_params)
            
            # Format results
            documents = []
            metadatas = []
            distances = []
            ids = []
            
            for result in results:
                documents.append(result["content"])
                metadatas.append({
                    "document_id": result.get("document_id"),
                    "title": result.get("title"),
                    "path": result.get("path"),
                    "file_type": result.get("file_type"),
                    "chunk_index": result.get("chunk_index")
                })
                # Azure AI Search doesn't provide distance scores directly
                # We'll use a placeholder or calculate from relevance score
                distances.append(1.0 - (result.get("@search.score", 0) / 100))
                ids.append(result["id"])
            
            return {
                "documents": [documents],
                "metadatas": [metadatas],
                "distances": [distances],
                "ids": [ids]
            }
            
        except Exception as e:
            logger.error(f"Azure AI Search error: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
    
    async def search_with_embeddings(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Search using vector embeddings
        
        Args:
            query_embedding: Query vector embedding
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            Search results
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create vector query
            vector_query = VectorizedQuery(
                vector=query_embedding,
                k_nearest_neighbors=n_results,
                fields="content_vector"
            )
            
            # Build filter expression
            filter_expr = None
            if filter_metadata:
                filter_parts = []
                for key, value in filter_metadata.items():
                    if isinstance(value, str):
                        filter_parts.append(f"{key} eq '{value}'")
                    else:
                        filter_parts.append(f"{key} eq {value}")
                filter_expr = " and ".join(filter_parts)
            
            # Perform vector search
            search_params = {
                "vector_queries": [vector_query],
                "vector_search_profile": "default-vector-profile",
                "top": n_results,
                "include_total_count": True
            }
            
            if filter_expr:
                search_params["filter"] = filter_expr
            
            results = self.search_client.search(**search_params)
            
            # Format results
            documents = []
            metadatas = []
            distances = []
            ids = []
            
            for result in results:
                documents.append(result["content"])
                metadatas.append({
                    "document_id": result.get("document_id"),
                    "title": result.get("title"),
                    "path": result.get("path"),
                    "file_type": result.get("file_type"),
                    "chunk_index": result.get("chunk_index")
                })
                distances.append(1.0 - (result.get("@search.score", 0) / 100))
                ids.append(result["id"])
            
            return {
                "documents": [documents],
                "metadatas": [metadatas],
                "distances": [distances],
                "ids": [ids]
            }
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
    
    async def delete_document(self, document_id: str):
        """
        Delete all chunks for a document
        
        Args:
            document_id: Document identifier
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Search for all chunks of the document
            results = self.search_client.search(
                search_text="*",
                filter=f"document_id eq '{document_id}'",
                select=["id"]
            )
            
            # Get all chunk IDs
            chunk_ids = [result["id"] for result in results]
            
            if chunk_ids:
                # Delete documents
                self.search_client.delete_documents(chunk_ids)
                logger.info(f"Deleted {len(chunk_ids)} chunks for document: {document_id}")
            
        except Exception as e:
            logger.error(f"Document deletion error: {e}")
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics
        
        Returns:
            Index statistics
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get index statistics
            stats = self.search_client.get_search_index_statistics()
            
            return {
                "total_documents": stats.document_count,
                "storage_size": stats.storage_size,
                "index_name": settings.azure_search_index_name,
                "initialized": self.initialized
            }
            
        except Exception as e:
            logger.error(f"Index stats error: {e}")
            return {"total_documents": 0, "storage_size": 0, "index_name": "unknown", "initialized": False}
    
    def _chunk_document(self, content: str, chunk_size: int = 500) -> List[str]:
        """
        Split document into overlapping chunks
        
        Args:
            content: Document content
            chunk_size: Target chunk size in words
            
        Returns:
            List of document chunks
        """
        
        words = content.split()
        chunks = []
        
        # Create overlapping chunks
        for i in range(0, len(words), chunk_size // 2):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
