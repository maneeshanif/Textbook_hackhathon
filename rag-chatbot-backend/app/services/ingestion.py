"""
Content ingestion service for batch embedding and Qdrant upload.
Handles chunking, embedding, and vector database insertion.
"""

import asyncio
from typing import List, Dict, Any
from qdrant_client.models import PointStruct

from app.gemini_client import gemini_client
from app.qdrant_client import qdrant_client
from app.middleware.logging import log_info, log_error


class IngestionService:
    """Service for ingesting textbook content into vector database."""
    
    def __init__(self):
        self.batch_size = 100  # Process 100 chunks at a time
    
    async def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for text chunks in batches.
        
        Args:
            chunks: List of chunks with text and metadata
        
        Returns:
            List of chunks with added embedding vectors
        """
        log_info(f"embedding_chunks_started", count=len(chunks))
        
        # Extract texts
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings in batches
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
            
            log_info(
                f"processing_batch",
                batch=batch_num,
                total_batches=total_batches,
                batch_size=len(batch_texts)
            )
            
            try:
                embeddings = await gemini_client.create_embeddings_batch(batch_texts)
                all_embeddings.extend(embeddings)
                
                # Small delay between batches to respect rate limits
                if i + self.batch_size < len(texts):
                    await asyncio.sleep(1)
            
            except Exception as e:
                log_error(
                    "batch_embedding_failed",
                    batch=batch_num,
                    error=str(e)
                )
                raise
        
        # Combine chunks with embeddings
        result = []
        for chunk, embedding in zip(chunks, all_embeddings):
            chunk_with_embedding = {
                **chunk,
                "vector": embedding
            }
            result.append(chunk_with_embedding)
        
        log_info("embedding_chunks_completed", count=len(result))
        return result
    
    async def upload_to_qdrant(
        self,
        chunks_with_embeddings: List[Dict[str, Any]],
        language: str = "en"
    ) -> None:
        """
        Upload chunks with embeddings to Qdrant collection.
        
        Args:
            chunks_with_embeddings: Chunks with vector embeddings and metadata
            language: Language code ('en' or 'ur')
        """
        log_info(
            "uploading_to_qdrant_started",
            count=len(chunks_with_embeddings),
            language=language
        )
        
        # Convert to PointStruct format
        points = []
        for i, chunk in enumerate(chunks_with_embeddings):
            point = PointStruct(
                id=i + 1,  # Start IDs from 1
                vector=chunk["vector"],
                payload=chunk["metadata"]
            )
            points.append(point)
        
        # Upload in batches
        for i in range(0, len(points), self.batch_size):
            batch_points = points[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(points) + self.batch_size - 1) // self.batch_size
            
            log_info(
                "uploading_batch",
                batch=batch_num,
                total_batches=total_batches,
                batch_size=len(batch_points)
            )
            
            try:
                await qdrant_client.upsert(batch_points, language=language)
                await asyncio.sleep(0.5)  # Rate limiting
            
            except Exception as e:
                log_error(
                    "batch_upload_failed",
                    batch=batch_num,
                    error=str(e)
                )
                raise
        
        log_info("uploading_to_qdrant_completed")
    
    async def ingest_content(
        self,
        chunks: List[Dict[str, Any]],
        language: str = "en"
    ) -> None:
        """
        Complete ingestion pipeline: embed and upload chunks.
        
        Args:
            chunks: Parsed text chunks with metadata
            language: Language code ('en' or 'ur')
        """
        log_info(
            "content_ingestion_started",
            total_chunks=len(chunks),
            language=language
        )
        
        # Step 1: Generate embeddings
        chunks_with_embeddings = await self.embed_chunks(chunks)
        
        # Step 2: Upload to Qdrant
        await self.upload_to_qdrant(chunks_with_embeddings, language=language)
        
        log_info("content_ingestion_completed")


# Global ingestion service instance
ingestion_service = IngestionService()
