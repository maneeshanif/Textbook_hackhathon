"""
RAG (Retrieval-Augmented Generation) service for chatbot queries.
Handles vector search, context retrieval, and streaming LLM responses.
"""

from typing import List, AsyncGenerator, Tuple
import re

from app.gemini_client import gemini_client
from app.qdrant_client import qdrant_client
from app.config import settings
from app.models.schemas import Citation, RAGResult
from app.middleware.logging import log_info, log_error


class RAGService:
    """Service for RAG-based question answering."""
    
    def __init__(self):
        self.similarity_threshold = settings.similarity_threshold
        self.max_chunks = settings.max_chunks
    
    async def search_relevant_chunks(
        self,
        query: str,
        language: str = "en",
        selected_text: str | None = None
    ) -> RAGResult:
        """
        Search for relevant textbook chunks using vector similarity.
        
        Args:
            query: User's question
            language: Language code ('en' or 'ur')
            selected_text: Optional text selection for contextual queries
        
        Returns:
            RAGResult with chunks, citations, and similarity scores
        """
        log_info(
            "vector_search_started",
            query=query[:100],
            language=language,
            has_selection=selected_text is not None
        )
        
        try:
            # Create query embedding
            query_vector = await gemini_client.create_embedding(query)
            
            # Search Qdrant
            search_results = await qdrant_client.search(
                query_vector=query_vector,
                language=language,
                limit=self.max_chunks,
                score_threshold=self.similarity_threshold
            )
            
            if not search_results:
                log_info("no_results_above_threshold", threshold=self.similarity_threshold)
                return RAGResult(chunks=[], citations=[], similarity_scores=[])
            
            # Extract chunks, citations, and scores
            chunks = []
            citations = []
            scores = []
            seen_chapters = set()
            
            for result in search_results:
                payload = result["payload"]
                score = result["score"]
                
                # Add chunk text (with selection context if provided)
                chunk_text = payload.get("text", "")
                if selected_text:
                    chunk_text = f"[Selected Text: {selected_text[:200]}...]\n\n{chunk_text}"
                
                chunks.append(chunk_text)
                scores.append(score)
                
                # Add unique citations
                chapter_id = payload.get("chapter_id", "")
                if chapter_id and chapter_id not in seen_chapters:
                    citation = Citation(
                        chapter_id=chapter_id,
                        title=payload.get("chapter_title", ""),
                        url=self._build_chapter_url(chapter_id, language)
                    )
                    citations.append(citation)
                    seen_chapters.add(chapter_id)
            
            log_info(
                "vector_search_completed",
                chunks_found=len(chunks),
                unique_citations=len(citations),
                avg_score=round(sum(scores) / len(scores), 3) if scores else 0
            )
            
            return RAGResult(
                chunks=chunks,
                citations=citations,
                similarity_scores=scores
            )
        
        except Exception as e:
            log_error("vector_search_failed", error=str(e))
            raise
    
    async def generate_streaming_response(
        self,
        query: str,
        rag_result: RAGResult,
        language: str = "en",
        user_preferences: dict | None = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming LLM response with context from RAG.
        
        Args:
            query: User's question
            rag_result: Retrieved chunks and citations
            language: Language code ('en' or 'ur')
            user_preferences: Optional user preferences (difficulty, focus_tags, preferred_language)
        
        Yields:
            Text chunks from LLM response
        """
        log_info("llm_generation_started", has_context=len(rag_result.chunks) > 0)
        
        try:
            if not rag_result.chunks:
                # No relevant context found - return fallback message
                fallback_msg = self._get_fallback_message(language)
                yield fallback_msg
                log_info("llm_generation_fallback")
                return
            
            # Generate streaming response with context and preferences
            async for chunk in gemini_client.generate_stream(
                prompt=query,
                context_chunks=rag_result.chunks,
                user_preferences=user_preferences
            ):
                yield chunk
            
            log_info("llm_generation_completed")
        
        except Exception as e:
            log_error("llm_generation_failed", error=str(e))
            raise
    
    async def query(
        self,
        query: str,
        language: str = "en",
        selected_text: str | None = None,
        user_preferences: dict | None = None
    ) -> Tuple[RAGResult, AsyncGenerator[str, None]]:
        """
        Complete RAG pipeline: search + generate streaming response.
        
        Args:
            query: User's question
            language: Language code ('en' or 'ur')
            selected_text: Optional text selection for contextual queries
            user_preferences: Optional user preferences for personalization
        
        Returns:
            Tuple of (RAGResult, streaming response generator)
        """
        # Step 1: Search for relevant chunks
        rag_result = await self.search_relevant_chunks(
            query=query,
            language=language,
            selected_text=selected_text
        )
        
        # Step 2: Generate streaming response with preferences
        response_stream = self.generate_streaming_response(
            query=query,
            rag_result=rag_result,
            language=language,
            user_preferences=user_preferences
        )
        
        return rag_result, response_stream
    
    def _build_chapter_url(self, chapter_id: str, language: str) -> str:
        """
        Build URL to chapter section.
        
        Args:
            chapter_id: Chapter identifier (e.g., '2.1.3')
            language: Language code ('en' or 'ur')
        
        Returns:
            Relative URL to the chapter
        """
        # Extract module and chapter from ID
        # Example: "2.1.3" -> module 2, chapter 1.3
        parts = chapter_id.split('.')
        if len(parts) >= 2:
            module = parts[0]
            chapter = '.'.join(parts[1:])
            
            # Build URL based on language
            if language == "ur":
                return f"/ur/docs/module-{module}/chapter-{chapter}"
            else:
                return f"/docs/module-{module}/chapter-{chapter}"
        
        # Fallback
        return f"/docs/{chapter_id}" if language == "en" else f"/ur/docs/{chapter_id}"
    
    def _get_fallback_message(self, language: str) -> str:
        """
        Get fallback message when no relevant content is found.
        
        Args:
            language: Language code ('en' or 'ur')
        
        Returns:
            Fallback message in the specified language
        """
        if language == "ur":
            return """معذرت، مجھے آپ کے سوال سے متعلق کتاب میں کوئی معلومات نہیں ملی۔ 
براہ کرم اپنا سوال مختلف الفاظ میں پوچھنے کی کوشش کریں یا Physical AI اور روبوٹکس سے متعلق کوئی اور سوال پوچھیں۔"""
        else:
            return """I couldn't find relevant information in the textbook for your question. 
This might be because:
- The topic isn't covered in the current chapters
- Your question is too broad or too specific
- There's a typo or unclear phrasing

Please try rephrasing your question or ask about topics related to Physical AI, robotics, kinematics, or control systems covered in the textbook."""


# Global RAG service instance
rag_service = RAGService()
