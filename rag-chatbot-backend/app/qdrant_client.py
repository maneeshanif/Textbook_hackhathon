"""
Qdrant async client wrapper for vector search operations.
Provides interface to Qdrant Cloud collections for English and Urdu content.
"""

from typing import List, Dict, Any
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter

from app.config import settings


# Collection names for different languages
COLLECTIONS = {
    "en": "textbook_chunks_en",
    "ur": "textbook_chunks_ur"
}

# Vector dimensions for Gemini text-embedding-004
VECTOR_SIZE = 768


class QdrantClientWrapper:
    """Wrapper for Qdrant async client operations."""
    
    def __init__(self):
        self.client: AsyncQdrantClient | None = None
    
    async def connect(self) -> None:
        """Initialize Qdrant async client on startup."""
        if self.client is None:
            self.client = AsyncQdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                timeout=30.0
            )
    
    async def disconnect(self) -> None:
        """Close Qdrant client on shutdown."""
        if self.client is not None:
            await self.client.close()
            self.client = None
    
    async def create_collection(self, language: str = "en") -> None:
        """
        Create a Qdrant collection for the specified language.
        
        Args:
            language: Language code ('en' or 'ur')
        """
        if self.client is None:
            raise RuntimeError("Qdrant client not initialized. Call connect() first.")
        
        collection_name = COLLECTIONS.get(language, COLLECTIONS["en"])
        
        # Check if collection already exists
        collections = await self.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if collection_name not in collection_names:
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
    
    async def search(
        self,
        query_vector: List[float],
        language: str = "en",
        limit: int = 5,
        score_threshold: float | None = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the specified collection.
        
        Args:
            query_vector: Query embedding vector (768 dimensions)
            language: Language code ('en' or 'ur')
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (default: from settings)
        
        Returns:
            List of search results with payload and similarity scores
        """
        if self.client is None:
            raise RuntimeError("Qdrant client not initialized. Call connect() first.")
        
        collection_name = COLLECTIONS.get(language, COLLECTIONS["en"])
        threshold = score_threshold or settings.similarity_threshold
        
        results = await self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=threshold
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            }
            for result in results
        ]
    
    async def upsert(
        self,
        points: List[PointStruct],
        language: str = "en"
    ) -> None:
        """
        Insert or update points in the specified collection.
        
        Args:
            points: List of PointStruct objects with id, vector, and payload
            language: Language code ('en' or 'ur')
        """
        if self.client is None:
            raise RuntimeError("Qdrant client not initialized. Call connect() first.")
        
        collection_name = COLLECTIONS.get(language, COLLECTIONS["en"])
        
        await self.client.upsert(
            collection_name=collection_name,
            points=points
        )
    
    async def delete_collection(self, language: str = "en") -> None:
        """
        Delete a Qdrant collection for the specified language.
        
        Args:
            language: Language code ('en' or 'ur')
        """
        if self.client is None:
            raise RuntimeError("Qdrant client not initialized. Call connect() first.")
        
        collection_name = COLLECTIONS.get(language, COLLECTIONS["en"])
        await self.client.delete_collection(collection_name=collection_name)
    
    async def health_check(self) -> bool:
        """
        Check Qdrant connectivity and health.
        
        Returns:
            True if Qdrant is healthy, False otherwise
        """
        try:
            if self.client is None:
                return False
            
            # Try to get collections list as a health check
            await self.client.get_collections()
            return True
        except Exception:
            return False


# Global Qdrant client instance
qdrant_client = QdrantClientWrapper()
