"""
Pydantic models for API request and response validation.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


# ========== Request Models ==========

class ChatQueryRequest(BaseModel):
    """Request model for chat query endpoint."""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question or query"
    )
    session_token: Optional[str] = Field(
        None,
        max_length=64,
        description="Session token for anonymous users"
    )
    language: str = Field(
        default="en",
        pattern="^(en|ur)$",
        description="Language preference (en or ur)"
    )
    selected_text: Optional[str] = Field(
        None,
        max_length=5000,
        description="Selected text for contextual queries"
    )


class FeedbackRequest(BaseModel):
    """Request model for feedback submission."""
    
    message_id: str = Field(
        ...,
        description="UUID of the message being rated"
    )
    rating: int = Field(
        ...,
        ge=-1,
        le=1,
        description="Rating: 1 for thumbs up, -1 for thumbs down"
    )
    feedback_text: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional text feedback"
    )
    
    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Ensure rating is either 1 or -1."""
        if v not in (1, -1):
            raise ValueError("Rating must be 1 (positive) or -1 (negative)")
        return v


class SessionMigrateRequest(BaseModel):
    """Request model for migrating localStorage session to database."""
    
    session_token: str = Field(
        ...,
        max_length=64,
        description="Session token from localStorage"
    )
    user_id: str = Field(
        ...,
        description="Authenticated user UUID"
    )


# ========== Response Models ==========

class Citation(BaseModel):
    """Citation model for textbook references."""
    
    chapter_id: str = Field(
        ...,
        description="Chapter identifier (e.g., '2.1.3')"
    )
    title: str = Field(
        ...,
        description="Chapter title"
    )
    url: str = Field(
        ...,
        description="URL to the chapter section"
    )


class ChatMessage(BaseModel):
    """Chat message model."""
    
    id: str = Field(
        ...,
        description="Message UUID"
    )
    role: str = Field(
        ...,
        pattern="^(user|assistant)$",
        description="Message sender: user or assistant"
    )
    content: str = Field(
        ...,
        description="Message text content"
    )
    citations: Optional[List[Citation]] = Field(
        None,
        description="Citations for assistant responses"
    )
    created_at: datetime = Field(
        ...,
        description="Message timestamp"
    )


class ChatQueryResponse(BaseModel):
    """Response model for chat query endpoint (non-streaming)."""
    
    message_id: str = Field(
        ...,
        description="UUID of the assistant's response message"
    )
    content: str = Field(
        ...,
        description="Assistant's response text"
    )
    citations: List[Citation] = Field(
        default_factory=list,
        description="Relevant chapter citations"
    )
    session_token: str = Field(
        ...,
        description="Session token for future requests"
    )


class ChatHistoryResponse(BaseModel):
    """Response model for chat history endpoint."""
    
    messages: List[ChatMessage] = Field(
        ...,
        description="List of chat messages in chronological order"
    )
    session_id: str = Field(
        ...,
        description="Session UUID"
    )
    has_more: bool = Field(
        ...,
        description="Whether more messages are available (pagination)"
    )
    total_count: int = Field(
        ...,
        description="Total number of messages in the session"
    )


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(
        ...,
        description="Overall health status: healthy or unhealthy"
    )
    services: Dict[str, bool] = Field(
        ...,
        description="Health status of individual services"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    
    success: bool = Field(
        ...,
        description="Whether feedback was successfully recorded"
    )
    feedback_id: str = Field(
        ...,
        description="UUID of the feedback record"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(
        ...,
        description="Error type/category"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    request_id: Optional[str] = Field(
        None,
        description="Request UUID for tracing"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )


# ========== Internal Models ==========

class ChunkMetadata(BaseModel):
    """Metadata for textbook chunks in vector database."""
    
    chapter_id: str = Field(
        ...,
        description="Chapter identifier (e.g., '2.1.3')"
    )
    chapter_title: str = Field(
        ...,
        description="Chapter title"
    )
    chunk_index: int = Field(
        ...,
        description="Index of chunk within the chapter"
    )
    file_path: str = Field(
        ...,
        description="Source MDX file path"
    )
    language: str = Field(
        ...,
        description="Content language (en or ur)"
    )


class RAGResult(BaseModel):
    """Result from RAG retrieval."""
    
    chunks: List[str] = Field(
        ...,
        description="Retrieved text chunks"
    )
    citations: List[Citation] = Field(
        ...,
        description="Citations for the chunks"
    )
    similarity_scores: List[float] = Field(
        ...,
        description="Similarity scores for each chunk"
    )


class MetricsData(BaseModel):
    """Metrics data for monitoring."""
    
    total_queries: int = Field(
        default=0,
        description="Total number of queries processed"
    )
    avg_response_time_ms: float = Field(
        default=0.0,
        description="Average response time in milliseconds"
    )
    p95_response_time_ms: float = Field(
        default=0.0,
        description="95th percentile response time in milliseconds"
    )
    error_rate: float = Field(
        default=0.0,
        description="Error rate as a percentage"
    )
    positive_feedback_rate: float = Field(
        default=0.0,
        description="Positive feedback rate as a percentage"
    )
