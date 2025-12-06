# API Contracts Summary

**Feature**: 003-rag-chatbot  
**Date**: 2025-12-06  
**Phase**: Phase 1 (Design)

## Overview

This directory contains API contract definitions for the RAG Chatbot backend. All endpoints follow RESTful conventions with JSON request/response bodies (except streaming endpoints which use Server-Sent Events).

---

## Endpoints Summary

### 1. Chat Operations

| Endpoint | Method | Purpose | Auth | Streaming |
|----------|--------|---------|------|-----------|
| `/api/chat/query` | POST | Submit query, get RAG response | Optional | ✅ SSE |
| `/api/chat/query-selection` | POST | Query with selected text context | Optional | ✅ SSE |
| `/api/chat/history` | GET | Retrieve session messages | Optional | ❌ |
| `/api/chat/migrate` | POST | Migrate anonymous → authenticated | Required | ❌ |
| `/api/chat/feedback` | POST | Submit thumbs up/down | Optional | ❌ |

### 2. Administrative Operations

| Endpoint | Method | Purpose | Auth | Streaming |
|----------|--------|---------|------|-----------|
| `/api/admin/ingest` | POST | Trigger content re-embedding | Admin Key | ❌ |
| `/api/health` | GET | Health check | None | ❌ |

---

## Authentication Flow

### Anonymous Users (Guest Mode)
```
1. Frontend generates session_token (UUID)
2. Stores session_token in localStorage
3. Includes session_token in chat/query requests
4. Backend creates chat_sessions row with user_id=NULL
```

### Authenticated Users
```
1. User signs in via Better Auth (OAuth)
2. Better Auth sets session cookie
3. Frontend calls /api/chat/migrate with localStorage messages
4. Backend updates session.user_id, creates messages
5. Future requests use session cookie (no session_token needed)
```

---

## Request/Response Patterns

### Standard JSON Response
```json
{
  "data": { /* response payload */ },
  "error": null,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "error": "validation_error",
  "message": "Query parameter 'language' is required",
  "details": {
    "field": "language",
    "constraint": "required"
  }
}
```

### Streaming Response (SSE)
```
data: {"chunk": "Forward kinematics"}

data: {"chunk": " is the process"}

data: {"citations": ["1.1.2", "1.2.1"]}

data: [DONE]
```

---

## Rate Limiting

**Tier-based limits:**
- Anonymous: 10 requests/minute per session_token
- Authenticated: 30 requests/minute per user_id
- Admin: 100 requests/minute per API key

**Headers:**
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 29
X-RateLimit-Reset: 1642248000
```

---

## CORS Configuration

**Allowed Origins (Production):**
- `https://physicalai-textbook.com`
- `https://www.physicalai-textbook.com`

**Allowed Origins (Development):**
- `http://localhost:3000`

**Allowed Methods:**
- `GET, POST, OPTIONS`

**Allowed Headers:**
- `Content-Type, Authorization, X-Session-Token`

---

## Validation Rules

### Query Text
- **Min Length**: 1 character
- **Max Length**: 1000 characters
- **Sanitization**: Strip HTML tags, trim whitespace

### Selected Text
- **Min Length**: 1 character
- **Max Length**: 5000 characters
- **Validation**: Must be substring of indexed content (optional check)

### Language Code
- **Allowed Values**: `en`, `ur`
- **Default**: `en` if omitted

### Session ID
- **Format**: UUID v4
- **Validation**: Must exist in chat_sessions table
- **Auto-creation**: If omitted, new session created

### Feedback Rating
- **Allowed Values**: `1` (positive), `-1` (negative)
- **Target Message**: Must be `role='assistant'`
- **Duplicate Prevention**: One rating per user per message (upsert)

---

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `validation_error` | Invalid request parameters |
| 401 | `unauthorized` | Authentication required or invalid |
| 404 | `not_found` | Resource not found (session, message) |
| 429 | `rate_limit_exceeded` | Too many requests |
| 500 | `internal_error` | Unexpected server error |
| 503 | `service_unavailable` | Dependency failure (Qdrant, Gemini API) |

---

## Monitoring & Observability

### Request Tracing
Every request generates a unique `request_id` (UUID) included in:
- Response headers: `X-Request-ID: req-abc123`
- Error responses: `details.request_id`
- Structured logs: `{"request_id": "req-abc123", ...}`

### Logged Metrics
- Request latency (p50, p95, p99)
- Vector search similarity scores
- Below-threshold queries (similarity < 0.7)
- Feedback distribution (positive vs negative)
- API endpoint usage by language

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "dependencies": {
    "postgres": "ok",
    "qdrant": "ok",
    "gemini": "ok"
  },
  "version": "1.0.0"
}
```

---

## Implementation Notes

### Streaming Response Handler (FastAPI)
```python
from fastapi.responses import StreamingResponse

async def stream_chat_response(query: str):
    async def event_generator():
        async for chunk in gemini_client.generate_content_stream(...):
            yield f"data: {json.dumps({'chunk': chunk.text})}\n\n"
        yield f"data: {json.dumps({'citations': citations})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### Session Token Hashing
```python
import hashlib

def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()[:64]
```

### Better Auth Session Validation
```python
async def get_current_user(request: Request) -> Optional[User]:
    session_cookie = request.cookies.get("better-auth.session_token")
    if not session_cookie:
        return None
    
    # Validate with Better Auth API
    response = await httpx.get(
        f"{BETTER_AUTH_URL}/api/auth/session",
        headers={"Cookie": f"better-auth.session_token={session_cookie}"}
    )
    
    if response.status_code != 200:
        return None
    
    session_data = response.json()
    return User(**session_data["user"])
```

---

## Testing Checklist

### Unit Tests (Endpoint Logic)
- [ ] Query endpoint with valid/invalid parameters
- [ ] Query-selection endpoint with empty selected_text
- [ ] History endpoint pagination edge cases
- [ ] Migration endpoint with duplicate messages
- [ ] Feedback endpoint with invalid message_id
- [ ] Ingestion endpoint with admin auth failure
- [ ] Health endpoint with dependency failures

### Integration Tests (End-to-End)
- [ ] Anonymous user full flow (query → history → feedback)
- [ ] Authenticated user flow (migrate → query → history)
- [ ] Streaming response delivery (SSE connection handling)
- [ ] Rate limiting enforcement (exceed limits, check headers)
- [ ] CORS preflight requests (OPTIONS method)
- [ ] Error handling (network failures, timeouts)

### Load Tests (Performance)
- [ ] 50 concurrent users (target: SC-006)
- [ ] Sustained 10 RPS for 5 minutes
- [ ] Streaming response under load
- [ ] Database connection pool exhaustion

---

**Status**: API Contracts Complete  
**Next Steps**: Generate quickstart.md (implementation sequence)  
**Dependencies**: OpenAPI spec can be imported into Postman/Insomnia for testing
