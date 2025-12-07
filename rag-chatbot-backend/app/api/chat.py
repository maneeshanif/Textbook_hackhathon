"""
Chat API endpoints for RAG-based question answering.
Handles query processing, history, feedback, and session management.
"""

import uuid
import hashlib
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import StreamingResponse
import json

from app.models.schemas import (
    ChatQueryRequest,
    ChatQueryResponse,
    ChatHistoryResponse,
    ChatMessage,
    FeedbackRequest,
    FeedbackResponse,
    SessionMigrateRequest,
    ErrorResponse
)
from app.services.rag import rag_service
from app.services.auth_service import AuthService
from app.database import db_pool
from app.middleware.logging import log_info, log_error, get_request_id


router = APIRouter()


async def get_current_user_optional(authorization: Optional[str] = Header(None)):
    """Get current user if authenticated, None otherwise."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    session_token = authorization.replace("Bearer ", "")
    auth_service = AuthService(db_pool.pool)
    user = await auth_service.verify_session(session_token)
    return user


def hash_session_token(token: str) -> str:
    """Hash session token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


async def get_or_create_session(
    session_token: Optional[str],
    language: str,
    user_id: Optional[str] = None
) -> tuple[str, str]:
    """
    Get existing session or create new one.
    
    Returns:
        Tuple of (session_id, session_token)
    """
    if session_token:
        # Try to find existing session by hashed token
        hashed_token = hash_session_token(session_token)
        
        session = await db_pool.fetchrow(
            """
            SELECT id FROM chat_sessions 
            WHERE session_token = $1
            """,
            hashed_token
        )
        
        if session:
            # Update last activity
            await db_pool.execute(
                "UPDATE chat_sessions SET last_activity = NOW() WHERE id = $1",
                session["id"]
            )
            return str(session["id"]), session_token
    
    # Create new session
    new_token = session_token or str(uuid.uuid4())
    hashed_token = hash_session_token(new_token)
    
    session_id = await db_pool.fetchval(
        """
        INSERT INTO chat_sessions (user_id, session_token, language)
        VALUES ($1, $2, $3)
        RETURNING id
        """,
        uuid.UUID(user_id) if user_id else None,
        hashed_token,
        language
    )
    
    log_info("session_created", session_id=str(session_id))
    return str(session_id), new_token


async def save_message(
    session_id: str,
    role: str,
    content: str,
    metadata: dict = None
) -> str:
    """
    Save a chat message to the database.
    
    Returns:
        Message ID
    """
    message_id = await db_pool.fetchval(
        """
        INSERT INTO chat_messages (session_id, role, content, metadata)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """,
        uuid.UUID(session_id),
        role,
        content,
        json.dumps(metadata or {})
    )
    
    return str(message_id)


@router.post("/chat/query")
async def chat_query(
    request: Request,
    query_request: ChatQueryRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Process a chat query with streaming response.
    
    Supports both authenticated and anonymous users.
    Authenticated users get personalized responses based on preferences.
    
    Request:
        - query: User's question (1-2000 chars)
        - session_token: Optional session token for history
        - language: Language preference ('en' or 'ur')
        - selected_text: Optional text selection for context
    
    Response:
        Server-Sent Events stream with:
        - data: Response chunks
        - [DONE] signal at end
        - metadata: Citations and session info
    """
    request_id = get_request_id(request)
    
    # Get authenticated user if present
    current_user = await get_current_user_optional(authorization)
    user_id = str(current_user.id) if current_user else None
    
    # Get user preferences if authenticated
    user_preferences = None
    if current_user:
        auth_service = AuthService(db_pool.pool)
        prefs = await auth_service.get_preferences(current_user.id)
        if prefs:
            user_preferences = {
                "difficulty": prefs.difficulty,
                "focus_tags": prefs.focus_tags,
                "preferred_language": prefs.preferred_language
            }
    
    log_info(
        "chat_query_started",
        query=query_request.query[:100],
        language=query_request.language,
        has_selection=query_request.selected_text is not None,
        authenticated=current_user is not None,
        user_id=user_id
    )
    
    try:
        # Get or create session
        session_id, session_token = await get_or_create_session(
            query_request.session_token,
            query_request.language,
            user_id=user_id
        )
        
        # Save user message
        user_message_id = await save_message(
            session_id=session_id,
            role="user",
            content=query_request.query
        )
        
        # Execute RAG pipeline with user preferences
        rag_result, response_stream = await rag_service.query(
            query=query_request.query,
            language=query_request.language,
            selected_text=query_request.selected_text,
            user_preferences=user_preferences
        )
        
        async def event_generator():
            """Generate SSE events for streaming response."""
            full_response = ""
            
            try:
                # Stream LLM response
                async for chunk in response_stream:
                    full_response += chunk
                    # Send chunk as SSE
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Save assistant message
                assistant_message_id = await save_message(
                    session_id=session_id,
                    role="assistant",
                    content=full_response,
                    metadata={
                        "citations": [c.dict() for c in rag_result.citations],
                        "similarity_scores": rag_result.similarity_scores
                    }
                )
                
                # Send completion metadata
                completion_data = {
                    "done": True,
                    "message_id": assistant_message_id,
                    "session_token": session_token,
                    "citations": [c.dict() for c in rag_result.citations]
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
                log_info(
                    "chat_query_completed",
                    message_id=assistant_message_id,
                    response_length=len(full_response),
                    citations_count=len(rag_result.citations)
                )
            
            except Exception as e:
                log_error("streaming_failed", error=str(e))
                error_data = {
                    "error": "streaming_failed",
                    "message": str(e),
                    "request_id": request_id
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )
    
    except Exception as e:
        log_error("chat_query_failed", error=str(e), error_type=type(e).__name__, traceback=True)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="internal_error",
                message="Failed to process query",
                request_id=request_id,
                details={"error": str(e)}
            ).dict()
        )


@router.get("/chat/history")
async def get_chat_history(
    session_token: str,
    limit: int = 50,
    offset: int = 0
):
    """
    Retrieve chat history for a session.
    
    Query Params:
        - session_token: Session identifier
        - limit: Maximum messages to return (default: 50)
        - offset: Pagination offset (default: 0)
    
    Response:
        ChatHistoryResponse with messages and pagination info
    """
    log_info("get_history_started", limit=limit, offset=offset)
    
    try:
        # Find session by token
        hashed_token = hash_session_token(session_token)
        session = await db_pool.fetchrow(
            """
            SELECT id FROM chat_sessions 
            WHERE session_token = $1
            """,
            hashed_token
        )
        
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        session_id = session["id"]
        
        # Get total message count
        total_count = await db_pool.fetchval(
            "SELECT COUNT(*) FROM chat_messages WHERE session_id = $1",
            session_id
        )
        
        # Get messages with pagination
        messages_rows = await db_pool.fetch(
            """
            SELECT id, role, content, metadata, created_at
            FROM chat_messages
            WHERE session_id = $1
            ORDER BY created_at ASC
            LIMIT $2 OFFSET $3
            """,
            session_id,
            limit,
            offset
        )
        
        # Convert to response format
        messages = []
        for row in messages_rows:
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
            
            message = ChatMessage(
                id=str(row["id"]),
                role=row["role"],
                content=row["content"],
                citations=metadata.get("citations"),
                created_at=row["created_at"]
            )
            messages.append(message)
        
        has_more = (offset + limit) < total_count
        
        log_info(
            "get_history_completed",
            messages_count=len(messages),
            total_count=total_count,
            has_more=has_more
        )
        
        return ChatHistoryResponse(
            messages=messages,
            session_id=str(session_id),
            has_more=has_more,
            total_count=total_count
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log_error("get_history_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve chat history"
        )


@router.post("/chat/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: Request, feedback: FeedbackRequest):
    """
    Submit feedback (thumbs up/down) for a message.
    
    Request:
        - message_id: UUID of the message
        - rating: 1 (positive) or -1 (negative)
        - feedback_text: Optional text feedback
    
    Response:
        FeedbackResponse with success status and feedback ID
    """
    request_id = get_request_id(request)
    
    log_info(
        "submit_feedback_started",
        message_id=feedback.message_id,
        rating=feedback.rating
    )
    
    try:
        # Verify message exists
        message = await db_pool.fetchrow(
            "SELECT id FROM chat_messages WHERE id = $1 AND role = 'assistant'",
            uuid.UUID(feedback.message_id)
        )
        
        if not message:
            raise HTTPException(
                status_code=404,
                detail="Message not found or not an assistant message"
            )
        
        # Insert feedback
        feedback_id = await db_pool.fetchval(
            """
            INSERT INTO feedback_ratings (message_id, rating, feedback_text)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            uuid.UUID(feedback.message_id),
            feedback.rating,
            feedback.feedback_text
        )
        
        log_info("submit_feedback_completed", feedback_id=str(feedback_id))
        
        return FeedbackResponse(
            success=True,
            feedback_id=str(feedback_id)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log_error("submit_feedback_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="internal_error",
                message="Failed to submit feedback",
                request_id=request_id
            ).dict()
        )


@router.post("/chat/migrate")
async def migrate_session(migrate_request: SessionMigrateRequest):
    """
    Migrate anonymous session to authenticated user.
    
    Request:
        - session_token: Anonymous session token
        - user_id: Authenticated user UUID
    
    Response:
        Success message
    """
    log_info(
        "migrate_session_started",
        user_id=migrate_request.user_id
    )
    
    try:
        # Find session
        hashed_token = hash_session_token(migrate_request.session_token)
        session = await db_pool.fetchrow(
            "SELECT id FROM chat_sessions WHERE session_token = $1",
            hashed_token
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session with user_id
        await db_pool.execute(
            """
            UPDATE chat_sessions
            SET user_id = $1, session_token = NULL
            WHERE id = $2
            """,
            uuid.UUID(migrate_request.user_id),
            session["id"]
        )
        
        log_info("migrate_session_completed")
        
        return {"success": True, "message": "Session migrated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        log_error("migrate_session_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to migrate session"
        )
