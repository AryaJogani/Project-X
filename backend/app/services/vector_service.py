"""
Vector service for semantic search and RAG using Azure AI Search
"""

from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings
from app.services.azure_search_service import AzureSearchService
from app.services.azure_openai_embeddings import AzureOpenAIEmbeddingsService

logger = logging.getLogger(__name__)

class VectorService:
    """
    Vector database service for semantic search and RAG using Azure AI Search
    """
    
    def __init__(self):
        self.azure_search = AzureSearchService()
        self.embeddings_service = AzureOpenAIEmbeddingsService()
        self.initialized = False
    
    async def initialize(self):
        """Initialize Azure AI Search service"""
        if self.initialized:
            return
            
        try:
            # Initialize Azure AI Search
            await self.azure_search.initialize()
            
            # Initialize Azure OpenAI embeddings
            await self.embeddings_service.initialize()
            
            self.initialized = True
            logger.info("✓ Vector service initialized with Azure AI Search and Azure OpenAI")
            
        except Exception as e:
            logger.error(f"❌ Vector service initialization failed: {e}")
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
            embeddings: Optional pre-computed embeddings for chunks
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Generate embeddings if not provided
            if embeddings is None:
                # Split content into chunks
                chunks = self._chunk_document(content, chunk_size=500)
                
                # Generate embeddings using Azure OpenAI
                embeddings = await self.embeddings_service.generate_embeddings(
                    texts=chunks,
                    model="text-embedding-3-large"
                )
            
            # Use Azure AI Search to index document
            await self.azure_search.index_document(
                document_id=document_id,
                content=content,
                metadata=metadata,
                embeddings=embeddings
            )
            
            logger.info(f"Indexed document chunks for: {document_id}")
            
        except Exception as e:
            logger.error(f"Document indexing error: {e}")
            raise
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Semantic search across knowledge base using Azure AI Search
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            Search results
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use Azure AI Search for semantic search
            results = await self.azure_search.search(
                query=query,
                n_results=n_results,
                filter_metadata=filter_metadata
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
    
    async def get_similar_chunks(
        self,
        chunk_id: str,
        n_results: int = 3
    ) -> Dict[str, Any]:
        """
        Get similar chunks to a specific chunk using Azure AI Search
        
        Args:
            chunk_id: ID of the reference chunk
            n_results: Number of similar chunks to return
            
        Returns:
            Similar chunks
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # First get the reference chunk content
            reference_results = await self.azure_search.search(
                query=f"id:{chunk_id}",
                n_results=1
            )
            
            if not reference_results["documents"][0]:
                return {"documents": [], "metadatas": [], "distances": [], "ids": []}
            
            # Search for similar content
            reference_content = reference_results["documents"][0][0]
            similar_results = await self.azure_search.search(
                query=reference_content,
                n_results=n_results + 1  # +1 to potentially exclude reference
            )
            
            # Filter out the reference chunk itself
            filtered_results = {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
                "ids": [[]]
            }
            
            for i, result_id in enumerate(similar_results["ids"][0]):
                if result_id != chunk_id:
                    filtered_results["documents"][0].append(similar_results["documents"][0][i])
                    filtered_results["metadatas"][0].append(similar_results["metadatas"][0][i])
                    filtered_results["distances"][0].append(similar_results["distances"][0][i])
                    filtered_results["ids"][0].append(result_id)
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Similar chunks search error: {e}")
            return {"documents": [], "metadatas": [], "distances": [], "ids": []}
    
    async def delete_document(self, document_id: str):
        """
        Delete all chunks for a document using Azure AI Search
        
        Args:
            document_id: Document identifier
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use Azure AI Search to delete document
            await self.azure_search.delete_document(document_id)
            
        except Exception as e:
            logger.error(f"Document deletion error: {e}")
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get index statistics from Azure AI Search
        
        Returns:
            Index statistics
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get stats from Azure AI Search
            stats = await self.azure_search.get_index_stats()
            
            return {
                "total_chunks": stats.get("total_documents", 0),
                "storage_size": stats.get("storage_size", 0),
                "index_name": stats.get("index_name", "unknown"),
                "initialized": self.initialized
            }
            
        except Exception as e:
            logger.error(f"Index stats error: {e}")
            return {"total_chunks": 0, "storage_size": 0, "index_name": "unknown", "initialized": False}
    
    async def search_with_embeddings(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Search using vector embeddings with Azure AI Search
        
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
            # Use Azure AI Search for vector search
            results = await self.azure_search.search_with_embeddings(
                query_embedding=query_embedding,
                n_results=n_results,
                filter_metadata=filter_metadata
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search with embeddings error: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
    
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
    
    async def search_with_reranking(
        self,
        query: str,
        n_results: int = 5,
        rerank_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Search with semantic reranking
        
        Args:
            query: Search query
            n_results: Number of results to return
            rerank_threshold: Minimum similarity score
            
        Returns:
            Reranked search results
        """
        
        # Get more results initially
        initial_results = await self.search(query, n_results * 2)
        
        # Filter by similarity threshold
        filtered_results = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
            "ids": [[]]
        }
        
        if initial_results["distances"][0]:
            for i, distance in enumerate(initial_results["distances"][0]):
                # Convert distance to similarity (lower distance = higher similarity)
                similarity = 1 - distance
                if similarity >= rerank_threshold:
                    filtered_results["documents"][0].append(initial_results["documents"][0][i])
                    filtered_results["metadatas"][0].append(initial_results["metadatas"][0][i])
                    filtered_results["distances"][0].append(distance)
                    filtered_results["ids"][0].append(initial_results["ids"][0][i])
        
        # Limit to requested number of results
        for key in filtered_results:
            filtered_results[key][0] = filtered_results[key][0][:n_results]
        
        return filtered_results
