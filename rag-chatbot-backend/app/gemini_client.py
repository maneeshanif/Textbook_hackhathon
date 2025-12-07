"""
Google Gemini API client for embeddings and chat completions.
Provides interface to Gemini text-embedding-004 and gemini-2.0-flash-exp models.
"""

import google.generativeai as genai
from typing import List, AsyncGenerator
import asyncio
from functools import partial

from app.config import settings


class GeminiClient:
    """Wrapper for Google Gemini API operations."""
    
    def __init__(self):
        self.embedding_model = None
        self.chat_model = None
        self._initialized = False
    
    def connect(self) -> None:
        """Initialize Gemini API client on startup."""
        if not self._initialized:
            # Configure API key
            genai.configure(api_key=settings.gemini_api_key)
            
            # Initialize embedding model
            self.embedding_model = genai.GenerativeModel('models/text-embedding-004')
            
            # Initialize chat model with streaming support
            self.chat_model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            self._initialized = True
    
    def disconnect(self) -> None:
        """Cleanup on shutdown (no persistent connection to close)."""
        self._initialized = False
        self.embedding_model = None
        self.chat_model = None
    
    async def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding vector for the given text.
        
        Args:
            text: Input text to embed (max 2048 tokens)
        
        Returns:
            768-dimensional embedding vector
        """
        if not self._initialized:
            raise RuntimeError("Gemini client not initialized. Call connect() first.")
        
        # Run embedding generation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            partial(
                genai.embed_content,
                model='models/text-embedding-004',
                content=text,
                task_type="retrieval_query"
            )
        )
        
        return result['embedding']
    
    async def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embedding vectors for multiple texts in batch.
        
        Args:
            texts: List of input texts to embed
        
        Returns:
            List of 768-dimensional embedding vectors
        """
        if not self._initialized:
            raise RuntimeError("Gemini client not initialized. Call connect() first.")
        
        # Process in batches to avoid rate limits
        embeddings = []
        batch_size = 100
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Run batch embedding in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                partial(
                    genai.embed_content,
                    model='models/text-embedding-004',
                    content=batch,
                    task_type="retrieval_document"
                )
            )
            
            embeddings.extend(result['embedding'])
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)
        
        return embeddings
    
    async def generate_stream(
        self,
        prompt: str,
        context_chunks: List[str] | None = None,
        user_preferences: dict | None = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming chat completion response.
        
        Args:
            prompt: User query/prompt
            context_chunks: Optional list of context chunks for RAG
            user_preferences: Optional user preferences (difficulty, focus_tags, preferred_language)
        
        Yields:
            Text chunks as they are generated
        """
        if not self._initialized:
            raise RuntimeError("Gemini client not initialized. Call connect() first.")
        
        # Build difficulty-specific instruction
        difficulty_instruction = ""
        if user_preferences and "difficulty" in user_preferences:
            diff = user_preferences["difficulty"]
            if diff == "beginner":
                difficulty_instruction = "- Explain concepts simply, avoid jargon, use analogies and examples\n"
            elif diff == "intermediate":
                difficulty_instruction = "- Balance technical depth with clarity, assume some robotics knowledge\n"
            elif diff == "advanced":
                difficulty_instruction = "- Provide detailed technical explanations, include equations and advanced concepts\n"
        
        # Build system message with context if provided
        full_prompt = prompt
        if context_chunks:
            context_text = "\n\n---\n\n".join([
                f"{chunk}"
                for chunk in context_chunks
            ])
            full_prompt = f"""You are an enthusiastic AI teaching assistant helping students learn about Physical AI and humanoid robotics from their textbook. 🤖

Here is relevant content from the textbook:

---
{context_text}
---

Student's question: {prompt}

Instructions:
- Answer using ONLY the information provided above
- Be clear, accurate, and educational
{difficulty_instruction}- Use relevant emojis (🤖 💡 ⚙️ 🎯 📊 🔧 ✨ 📚 etc.) to make explanations engaging and highlight key points
- Explain concepts step-by-step when appropriate
- Break down complex topics with examples
- If the content doesn't fully answer the question, acknowledge this honestly
- Do NOT mention "Context 1", "Context 2", or reference placeholder text
- Write naturally as if teaching a curious student

Your answer:"""
        
        # Generate streaming response
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            partial(
                self.chat_model.generate_content,
                full_prompt,
                stream=True
            )
        )
        
        # Yield chunks as they arrive
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    async def health_check(self) -> bool:
        """
        Check Gemini API connectivity and health.
        
        Returns:
            True if Gemini API is healthy, False otherwise
        """
        try:
            if not self._initialized:
                return False
            
            # Try a simple embedding as health check
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                partial(
                    genai.embed_content,
                    model='models/text-embedding-004',
                    content="health check",
                    task_type="retrieval_query"
                )
            )
            return True
        except Exception:
            return False


# Global Gemini client instance
gemini_client = GeminiClient()
