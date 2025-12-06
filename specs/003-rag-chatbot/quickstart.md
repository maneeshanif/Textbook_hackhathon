# Implementation Quickstart: RAG Chatbot

**Feature**: 003-rag-chatbot  
**Date**: 2025-12-06  
**Phase**: Phase 1 (Design)  
**Estimated Timeline**: 8 phases over 5-7 days

## Overview

This document provides a step-by-step implementation sequence for building the RAG chatbot. Each phase delivers a testable increment with clear acceptance criteria. Designed for rapid prototyping in a hackathon environment.

**Dependencies Flow:**
```
Phase 1 (Foundation) → Phase 2 (Ingestion) → Phase 3 (Core RAG)
         ↓                                          ↓
Phase 4 (History) → Phase 5 (Auth) → Phase 6 (Frontend)
                                          ↓
                    Phase 7 (Observability) → Phase 8 (Bonus)
```

---

## Phase 1: Backend Foundation (Day 1, 2-3 hours)

**Goal**: Set up FastAPI project with health check and database connections.

### Tasks
1. **Initialize FastAPI project**
   ```bash
   mkdir rag-chatbot-backend && cd rag-chatbot-backend
   python -m venv venv && source venv/bin/activate
   pip install fastapi uvicorn asyncpg qdrant-client google-genai python-dotenv pydantic-settings
   ```

2. **Create project structure**
   ```
   rag-chatbot-backend/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py          # FastAPI app entry point
   │   ├── config.py        # Settings (env vars)
   │   ├── database.py      # Postgres connection pool
   │   └── api/
   │       ├── __init__.py
   │       └── health.py    # Health check endpoint
   ├── .env.example
   └── requirements.txt
   ```

3. **Configure environment variables** (`.env`)
   ```env
   # Database
   NEON_CONNECTION_STRING=postgresql://user:pass@host/db
   
   # Qdrant
   QDRANT_URL=https://xxx.qdrant.io
   QDRANT_API_KEY=your-api-key
   
   # Google Gemini
   GEMINI_API_KEY=<your-api-key>
   
   # App
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

4. **Implement health check endpoint**
   ```python
   # app/api/health.py
   from fastapi import APIRouter
   from app.database import db_pool
   from app.qdrant_client import qdrant_client
   
   router = APIRouter()
   
   @router.get("/api/health")
   async def health_check():
       dependencies = {}
       
       # Check Postgres
       try:
           async with db_pool.acquire() as conn:
               await conn.fetchval("SELECT 1")
           dependencies["postgres"] = "ok"
       except Exception as e:
           dependencies["postgres"] = "error"
       
       # Check Qdrant
       try:
           await qdrant_client.get_collections()
           dependencies["qdrant"] = "ok"
       except Exception as e:
           dependencies["qdrant"] = "error"
       
       # Check Gemini (lightweight ping)
       dependencies["gemini"] = "ok"  # Assume ok, check on first query
       
       status = "healthy" if all(v == "ok" for v in dependencies.values()) else "degraded"
       
       return {
           "status": status,
           "dependencies": dependencies,
           "version": "1.0.0"
       }
   ```

5. **Run migrations**
   ```bash
   psql $NEON_CONNECTION_STRING < migrations/001_init_schema.sql
   ```

### Acceptance Criteria
- [ ] `GET /api/health` returns 200 with all dependencies "ok"
- [ ] Database connection pool successfully connects to Neon
- [ ] Qdrant client successfully connects to cloud instance
- [ ] Environment variables loaded correctly

### Testing
```bash
# Start server
uvicorn app.main:app --reload

# Test health check
curl http://localhost:8000/api/health
```

---

## Phase 2: Content Ingestion Pipeline (Day 1-2, 3-4 hours)

**Goal**: Parse MDX files, generate embeddings, and store in Qdrant.

### Tasks
1. **Install additional dependencies**
   ```bash
   pip install unified remark-parse remark-gfm tiktoken
   ```

2. **Create ingestion script** (`scripts/ingest_textbook.py`)
   ```python
   import asyncio
   from pathlib import Path
   from google import genai
   from qdrant_client import AsyncQdrantClient
   from qdrant_client.models import PointStruct, Distance, VectorParams
   
   # Parse MDX file (exclude code blocks)
   def parse_mdx(file_path: Path) -> list[dict]:
       """Extract text chunks from MDX, excluding code blocks."""
       # Implementation: Use remark/unified to parse MDX
       # Split into 500-token chunks with 50-token overlap
       pass
   
   # Generate embeddings
   async def embed_text(texts: list[str]) -> list[list[float]]:
       client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
       response = client.models.embed_content(
           model="text-embedding-004",
           contents=texts
       )
       return [emb.values for emb in response.embeddings]
   
   # Upsert to Qdrant
   async def upsert_chunks(collection_name: str, chunks: list[dict]):
       client = AsyncQdrantClient(...)
       
       # Create collection if not exists
       collections = await client.get_collections()
       if collection_name not in [c.name for c in collections.collections]:
           await client.create_collection(
               collection_name=collection_name,
               vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
           )
       
       # Generate embeddings
       texts = [chunk["text"] for chunk in chunks]
       embeddings = await embed_text(texts)
       
       # Prepare points
       points = [
           PointStruct(
               id=chunk["id"],
               vector=embedding,
               payload=chunk["payload"]
           )
           for chunk, embedding in zip(chunks, embeddings)
       ]
       
       # Upsert
       await client.upsert(collection_name=collection_name, points=points)
   ```

3. **Implement admin ingestion endpoint** (`app/api/admin.py`)
   ```python
   from fastapi import APIRouter, Header, HTTPException
   from app.config import settings
   
   router = APIRouter()
   
   @router.post("/api/admin/ingest")
   async def trigger_ingestion(
       languages: list[str],
       force_reindex: bool = False,
       x_api_key: str = Header(...)
   ):
       if x_api_key != settings.ADMIN_API_KEY:
           raise HTTPException(status_code=401, detail="Invalid API key")
       
       # Run ingestion script
       result = await ingest_content(languages, force_reindex)
       return result
   ```

### Acceptance Criteria
- [ ] Parse English MDX files (400+ chunks)
- [ ] Parse Urdu MDX files (400+ chunks)
- [ ] Generate embeddings for all chunks
- [ ] Upsert to `textbook_chunks_en` and `textbook_chunks_ur` collections
- [ ] Each point has correct payload (text, chapter, section, module, week, language)
- [ ] Ingestion script is idempotent (can re-run without duplicates)

### Testing
```bash
# Run ingestion locally
python scripts/ingest_textbook.py --language en --path ../book/docs
python scripts/ingest_textbook.py --language ur --path ../book/i18n/ur/docusaurus-plugin-content-docs/current

# Verify in Qdrant dashboard
# - Check collection sizes (400+ points each)
# - Sample payload fields
```

---

## Phase 3: Core RAG Endpoint (Day 2-3, 4-5 hours)

**Goal**: Implement vector search + LLM streaming response with citations.

### Tasks
1. **Create chat endpoint** (`app/api/chat.py`)
   ```python
   from fastapi import APIRouter
   from fastapi.responses import StreamingResponse
   from app.services.rag import RAGService
   
   router = APIRouter()
   rag_service = RAGService()
   
   @router.post("/api/chat/query")
   async def chat_query(request: ChatQueryRequest):
       # Validate session
       session = await get_or_create_session(
           session_id=request.session_id,
           session_token=request.session_token,
           language=request.language
       )
       
       # Stream response
       return StreamingResponse(
           rag_service.stream_response(
               query=request.query,
               language=request.language,
               session_id=session.id
           ),
           media_type="text/event-stream"
       )
   ```

2. **Implement RAG service** (`app/services/rag.py`)
   ```python
   from google import genai
   from qdrant_client import AsyncQdrantClient
   from qdrant_client.models import Filter, FieldCondition, MatchValue
   
   class RAGService:
       def __init__(self):
           self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
           self.qdrant_client = AsyncQdrantClient(...)
       
       async def stream_response(self, query: str, language: str, session_id: str):
           # 1. Embed query
           query_embedding = await self.embed_query(query)
           
           # 2. Search Qdrant
           search_results = await self.qdrant_client.search(
               collection_name=f"textbook_chunks_{language}",
               query_vector=query_embedding,
               query_filter=Filter(
                   must=[FieldCondition(key="language", match=MatchValue(value=language))]
               ),
               limit=5,
               score_threshold=0.7  # FR-004
           )
           
           # 3. Build context
           context = "\n\n".join([
               f"[{hit.payload['chapter']}] {hit.payload['text']}"
               for hit in search_results
           ])
           citations = [hit.payload["chapter"] for hit in search_results]
           
           # 4. Generate streaming response
           messages = [
               {"role": "system", "content": "You are a helpful AI assistant..."},
               {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
           ]
           
           full_response = ""
           for chunk in self.gemini_client.models.generate_content_stream(
               model="gemini-2.0-flash-exp",
               contents=messages[-1]["content"]  # Gemini uses simpler format
           ):
               if chunk.text:
                   full_response += chunk.text
                   yield f"data: {json.dumps({'chunk': chunk.text})}\n\n"
           
           # 5. Send citations
           yield f"data: {json.dumps({'citations': citations})}\n\n"
           yield "data: [DONE]\n\n"
           
           # 6. Save messages to database
           await self.save_messages(session_id, query, full_response, citations)
       
       async def embed_query(self, query: str) -> list[float]:
           response = self.gemini_client.models.embed_content(
               model="text-embedding-004",
               contents=query
           )
           return response.embeddings[0].values
       
       async def save_messages(self, session_id, query, response, citations):
           async with db_pool.acquire() as conn:
               # Insert user message
               await conn.execute(
                   "INSERT INTO chat_messages (session_id, role, content) VALUES ($1, $2, $3)",
                   session_id, "user", query
               )
               
               # Insert assistant message
               await conn.execute(
                   "INSERT INTO chat_messages (session_id, role, content, metadata) VALUES ($1, $2, $3, $4)",
                   session_id, "assistant", response, json.dumps({"citations": citations})
               )
   ```

3. **Implement query-selection endpoint**
   ```python
   @router.post("/api/chat/query-selection")
   async def query_selection(request: QuerySelectionRequest):
       # Same as chat_query, but prepend selected_text to context
       augmented_query = f"Selected text: {request.selected_text}\n\nQuestion: {request.query}"
       # ... rest of RAG flow
   ```

### Acceptance Criteria
- [ ] Vector search returns top 5 results with similarity >= 0.7
- [ ] Streaming response delivers chunks in real-time (< 100ms latency between chunks)
- [ ] Citations included in final SSE message
- [ ] User and assistant messages saved to chat_messages table
- [ ] Query-selection endpoint includes selected text in context
- [ ] Below-threshold queries logged (FR-021)

### Testing
```bash
# Test basic query
curl -N -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is forward kinematics?", "language": "en", "session_token": "test-token-123"}'

# Expected output (SSE stream):
# data: {"chunk": "Forward"}
# data: {"chunk": " kinematics"}
# ...
# data: {"citations": ["1.1.2"]}
# data: [DONE]
```

---

## Phase 4: Chat History & Cleanup (Day 3, 2-3 hours)

**Goal**: Implement history retrieval and 90-day retention for anonymous sessions.

### Tasks
1. **Implement history endpoint** (`app/api/chat.py`)
   ```python
   @router.get("/api/chat/history")
   async def get_history(
       session_id: str = None,
       session_token: str = None,
       limit: int = 20,
       offset: int = 0
   ):
       # Validate session ownership
       session = await validate_session(session_id, session_token)
       
       # Fetch messages
       async with db_pool.acquire() as conn:
           rows = await conn.fetch(
               """
               SELECT id, role, content, metadata, created_at
               FROM chat_messages
               WHERE session_id = $1
               ORDER BY created_at DESC
               LIMIT $2 OFFSET $3
               """,
               session.id, limit, offset
           )
           
           total = await conn.fetchval(
               "SELECT COUNT(*) FROM chat_messages WHERE session_id = $1",
               session.id
           )
       
       messages = [dict(row) for row in rows]
       return {
           "session_id": session.id,
           "messages": messages,
           "total_count": total,
           "has_more": (offset + limit) < total
       }
   ```

2. **Create cleanup job** (`scripts/cleanup_sessions.py`)
   ```python
   import asyncio
   import asyncpg
   from datetime import datetime, timedelta
   
   async def cleanup_old_sessions():
       """Delete anonymous sessions older than 90 days."""
       conn = await asyncpg.connect(os.getenv("NEON_CONNECTION_STRING"))
       
       cutoff_date = datetime.utcnow() - timedelta(days=90)
       
       deleted_sessions = await conn.fetch(
           """
           DELETE FROM chat_sessions
           WHERE user_id IS NULL AND created_at < $1
           RETURNING id
           """,
           cutoff_date
       )
       
       print(f"Deleted {len(deleted_sessions)} anonymous sessions")
       await conn.close()
   
   if __name__ == "__main__":
       asyncio.run(cleanup_old_sessions())
   ```

3. **Schedule cron job** (production)
   ```bash
   # Add to crontab (runs daily at 2 AM)
   0 2 * * * /path/to/venv/bin/python /path/to/scripts/cleanup_sessions.py
   ```

### Acceptance Criteria
- [ ] History endpoint returns messages in reverse chronological order
- [ ] Pagination works correctly (limit/offset)
- [ ] Anonymous users can access history with session_token
- [ ] Authenticated users can access all their sessions
- [ ] Cleanup script deletes sessions older than 90 days
- [ ] Cascade deletion removes associated messages and feedback

### Testing
```bash
# Test history retrieval
curl "http://localhost:8000/api/chat/history?session_token=test-token-123&limit=10"

# Test cleanup script
python scripts/cleanup_sessions.py
# Check database: SELECT COUNT(*) FROM chat_sessions WHERE user_id IS NULL AND created_at < NOW() - INTERVAL '90 days';
```

---

## Phase 5: Authentication Integration (Day 3-4, 3-4 hours)

**Goal**: Integrate Better Auth for user sessions and implement migration endpoint.

### Tasks
1. **Set up Better Auth** (separate service or in-app)
   ```bash
   # Option 1: Separate Node.js service (recommended)
   cd better-auth-service
   npm install better-auth @better-auth/core
   npm run dev  # Runs on port 3001
   
   # Option 2: Use Better Auth REST API directly from Python
   # No local service needed, just HTTP calls
   ```

2. **Implement session validation middleware** (`app/middleware/auth.py`)
   ```python
   import httpx
   from fastapi import Request, HTTPException
   from app.config import settings
   
   async def get_current_user(request: Request) -> Optional[dict]:
       """Validate session cookie with Better Auth API."""
       session_cookie = request.cookies.get("better-auth.session_token")
       if not session_cookie:
           return None
       
       async with httpx.AsyncClient() as client:
           response = await client.get(
               f"{settings.BETTER_AUTH_URL}/api/auth/session",
               headers={"Cookie": f"better-auth.session_token={session_cookie}"}
           )
       
       if response.status_code != 200:
           return None
       
       session_data = response.json()
       return session_data.get("user")
   ```

3. **Implement migration endpoint** (`app/api/chat.py`)
   ```python
   @router.post("/api/chat/migrate")
   async def migrate_session(request: MigrateSessionRequest, current_user: dict = Depends(get_current_user)):
       if not current_user:
           raise HTTPException(status_code=401, detail="Authentication required")
       
       async with db_pool.acquire() as conn:
           # Find or create user in database
           user_id = await conn.fetchval(
               "INSERT INTO users (id, email, name) VALUES ($1, $2, $3) ON CONFLICT (id) DO UPDATE SET updated_at = NOW() RETURNING id",
               current_user["id"], current_user["email"], current_user.get("name")
           )
           
           # Update session
           session = await conn.fetchrow(
               "UPDATE chat_sessions SET user_id = $1, session_token = NULL WHERE session_token = $2 RETURNING id",
               user_id, hash_session_token(request.session_token)
           )
           
           if not session:
               raise HTTPException(status_code=404, detail="Session not found")
           
           # Insert migrated messages
           for msg in request.messages:
               await conn.execute(
                   "INSERT INTO chat_messages (session_id, role, content, metadata, created_at) VALUES ($1, $2, $3, $4, $5)",
                   session["id"], msg["role"], msg["content"], msg.get("metadata", {}), msg["created_at"]
               )
       
       return {
           "session_id": session["id"],
           "messages_migrated": len(request.messages),
           "message": "Session migrated successfully"
       }
   ```

### Acceptance Criteria
- [ ] Better Auth session validation works via middleware
- [ ] Authenticated users can access their sessions
- [ ] Migration endpoint transfers localStorage messages to database
- [ ] Guest users can upgrade to authenticated accounts
- [ ] Authenticated sessions excluded from 90-day cleanup

### Testing
```bash
# Test authentication flow
# 1. Sign in via Better Auth UI
# 2. Get session cookie
# 3. Call migrate endpoint with localStorage messages

curl -X POST http://localhost:8000/api/chat/migrate \
  -H "Content-Type: application/json" \
  -H "Cookie: better-auth.session_token=..." \
  -d '{"session_token": "test-token-123", "messages": [...]}'
```

---

## Phase 6: Frontend Chat Widget (Day 4-5, 4-6 hours)

**Goal**: Build React chat widget embedded in Docusaurus with localStorage fallback.

### Tasks
1. **Create chat widget component** (`book/src/components/ChatWidget/index.tsx`)
   ```tsx
   import React, { useState, useEffect } from 'react';
   import { EventSourcePolyfill } from 'event-source-polyfill';
   
   export default function ChatWidget() {
     const [messages, setMessages] = useState([]);
     const [input, setInput] = useState('');
     const [sessionToken, setSessionToken] = useState(null);
     const [language, setLanguage] = useState('en');
     
     useEffect(() => {
       // Load from localStorage
       const saved = localStorage.getItem('chat-session');
       if (saved) {
         const { token, history } = JSON.parse(saved);
         setSessionToken(token);
         setMessages(history);
       } else {
         // Generate new session token
         const newToken = crypto.randomUUID();
         setSessionToken(newToken);
         localStorage.setItem('chat-session', JSON.stringify({ token: newToken, history: [] }));
       }
     }, []);
     
     const handleSubmit = async (e) => {
       e.preventDefault();
       if (!input.trim()) return;
       
       // Add user message
       const userMsg = { role: 'user', content: input, created_at: new Date().toISOString() };
       setMessages(prev => [...prev, userMsg]);
       
       // Stream assistant response
       const assistantMsg = { role: 'assistant', content: '', citations: [], created_at: new Date().toISOString() };
       setMessages(prev => [...prev, assistantMsg]);
       
       const eventSource = new EventSourcePolyfill('http://localhost:8000/api/chat/query', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ query: input, language, session_token: sessionToken })
       });
       
       eventSource.onmessage = (event) => {
         if (event.data === '[DONE]') {
           eventSource.close();
           // Save to localStorage
           localStorage.setItem('chat-session', JSON.stringify({ token: sessionToken, history: messages }));
           return;
         }
         
         const data = JSON.parse(event.data);
         if (data.chunk) {
           setMessages(prev => {
             const last = prev[prev.length - 1];
             return [...prev.slice(0, -1), { ...last, content: last.content + data.chunk }];
           });
         } else if (data.citations) {
           setMessages(prev => {
             const last = prev[prev.length - 1];
             return [...prev.slice(0, -1), { ...last, citations: data.citations }];
           });
         }
       };
       
       setInput('');
     };
     
     return (
       <div className="chat-widget">
         <div className="messages">
           {messages.map((msg, i) => (
             <div key={i} className={`message ${msg.role}`}>
               <p>{msg.content}</p>
               {msg.citations && <div className="citations">Sources: {msg.citations.join(', ')}</div>}
             </div>
           ))}
         </div>
         <form onSubmit={handleSubmit}>
           <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask a question..." />
           <button type="submit">Send</button>
         </form>
       </div>
     );
   }
   ```

2. **Embed widget in Docusaurus** (swizzle or global component)
   ```bash
   cd book
   npm run swizzle @docusaurus/theme-classic Footer -- --eject
   ```
   
   Edit `src/theme/Footer/index.tsx`:
   ```tsx
   import ChatWidget from '@site/src/components/ChatWidget';
   
   export default function Footer() {
     return (
       <>
         <ChatWidget />
         {/* ... existing footer */}
       </>
     );
   }
   ```

3. **Implement text selection handler** (`book/src/components/ChatWidget/SelectionHandler.tsx`)
   ```tsx
   useEffect(() => {
     const handleSelection = () => {
       const selection = window.getSelection();
       const selectedText = selection?.toString().trim();
       if (selectedText && selectedText.length > 10) {
         setSelectedText(selectedText);
         setShowSelectionPrompt(true);
       }
     };
     
     document.addEventListener('mouseup', handleSelection);
     return () => document.removeEventListener('mouseup', handleSelection);
   }, []);
   ```

### Acceptance Criteria
- [ ] Chat widget renders in Docusaurus footer
- [ ] Messages persisted in localStorage for anonymous users
- [ ] Text selection triggers query prompt
- [ ] Streaming responses display in real-time
- [ ] Citations displayed as clickable chapter links
- [ ] Language toggle switches between English/Urdu

### Testing
```bash
# Run Docusaurus with widget
cd book
npm run start

# Manual testing:
# 1. Ask a question → check streaming response
# 2. Refresh page → verify localStorage persistence
# 3. Select text → verify query prompt appears
# 4. Sign in → verify migration prompt appears
```

---

## Phase 7: Observability (Day 5, 2-3 hours)

**Goal**: Add structured logging, metrics collection, and monitoring.

### Tasks
1. **Install logging dependencies**
   ```bash
   pip install structlog
   ```

2. **Configure structured logging** (`app/logging.py`)
   ```python
   import structlog
   import logging
   
   def configure_logging():
       structlog.configure(
           processors=[
               structlog.stdlib.add_log_level,
               structlog.processors.TimeStamper(fmt="iso"),
               structlog.processors.StackInfoRenderer(),
               structlog.processors.format_exc_info,
               structlog.processors.JSONRenderer()
           ],
           wrapper_class=structlog.stdlib.BoundLogger,
           logger_factory=structlog.stdlib.LoggerFactory(),
       )
       
       logging.basicConfig(format="%(message)s", level=logging.INFO)
   ```

3. **Add request tracing middleware** (`app/middleware/logging.py`)
   ```python
   from starlette.middleware.base import BaseHTTPMiddleware
   import structlog
   import uuid
   import time
   
   class RequestLoggingMiddleware(BaseHTTPMiddleware):
       async def dispatch(self, request, call_next):
           request_id = str(uuid.uuid4())
           request.state.request_id = request_id
           
           logger = structlog.get_logger()
           logger = logger.bind(request_id=request_id, method=request.method, path=request.url.path)
           
           start_time = time.time()
           response = await call_next(request)
           duration = time.time() - start_time
           
           logger.info("request_completed", status_code=response.status_code, duration_ms=int(duration * 1000))
           
           response.headers["X-Request-ID"] = request_id
           return response
   ```

4. **Implement metrics collector** (`app/services/metrics.py`)
   ```python
   from collections import defaultdict
   import statistics
   
   class MetricsCollector:
       def __init__(self):
           self.latencies = []
           self.similarity_scores = []
           self.below_threshold_queries = []
       
       def record_latency(self, latency_ms: int):
           self.latencies.append(latency_ms)
       
       def record_similarity(self, scores: list[float]):
           self.similarity_scores.extend(scores)
           if max(scores) < 0.7:
               self.below_threshold_queries.append(scores)
       
       def get_stats(self):
           return {
               "latency_p50": statistics.median(self.latencies) if self.latencies else 0,
               "latency_p95": self.percentile(self.latencies, 95) if self.latencies else 0,
               "latency_p99": self.percentile(self.latencies, 99) if self.latencies else 0,
               "avg_similarity": statistics.mean(self.similarity_scores) if self.similarity_scores else 0,
               "below_threshold_count": len(self.below_threshold_queries)
           }
       
       @staticmethod
       def percentile(data, p):
           data.sort()
           k = (len(data) - 1) * (p / 100)
           f = int(k)
           c = f + 1 if f < len(data) - 1 else f
           return data[f] + (k - f) * (data[c] - data[f])
   
   metrics = MetricsCollector()
   ```

5. **Add metrics endpoint** (`app/api/admin.py`)
   ```python
   @router.get("/api/admin/metrics")
   async def get_metrics(x_api_key: str = Header(...)):
       if x_api_key != settings.ADMIN_API_KEY:
           raise HTTPException(status_code=401)
       
       return metrics.get_stats()
   ```

### Acceptance Criteria
- [ ] All requests logged in JSON format with request_id
- [ ] Latency tracked for chat queries (p50, p95, p99)
- [ ] Similarity scores logged for quality analysis
- [ ] Below-threshold queries tracked (FR-021)
- [ ] Metrics endpoint returns aggregated stats
- [ ] X-Request-ID header included in all responses

### Testing
```bash
# Check logs (JSON format)
tail -f logs/app.log | jq

# Query metrics endpoint
curl -H "X-API-Key: admin-key" http://localhost:8000/api/admin/metrics
```

---

## Phase 8: Bonus Features (Day 6-7, Optional)

**Goal**: Implement nice-to-have features (Urdu support, personalization, cross-device sync).

### Tasks
1. **Multi-language support (FR-023)**
   - Already implemented via language parameter in queries
   - Test Urdu content ingestion and retrieval
   - Add language toggle in chat widget UI

2. **Personalization (FR-027)**
   ```python
   # Store user preferences
   async def save_user_preferences(user_id: str, preferences: dict):
       await conn.execute(
           "UPDATE users SET preferences = $1 WHERE id = $2",
           json.dumps(preferences), user_id
       )
   
   # Retrieve preferences
   async def get_user_preferences(user_id: str) -> dict:
       row = await conn.fetchrow("SELECT preferences FROM users WHERE id = $1", user_id)
       return json.loads(row["preferences"]) if row else {}
   ```

3. **Cross-device sync (FR-028)**
   - Already implemented via authenticated sessions
   - Test accessing history from different devices
   - Add device fingerprinting for security

4. **Feedback collection (FR-018)**
   ```tsx
   // Add thumbs up/down buttons to assistant messages
   <div className="feedback-buttons">
     <button onClick={() => submitFeedback(msg.id, 1)}>👍</button>
     <button onClick={() => submitFeedback(msg.id, -1)}>👎</button>
   </div>
   ```

5. **Admin analytics dashboard (SC-007)**
   ```python
   @router.get("/api/admin/analytics")
   async def get_analytics():
       async with db_pool.acquire() as conn:
           # Positive feedback rate
           feedback_rate = await conn.fetchval(
               "SELECT COUNT(*) FILTER (WHERE rating = 1)::FLOAT / COUNT(*) FROM feedback_ratings"
           )
           
           # Total queries
           total_queries = await conn.fetchval("SELECT COUNT(*) FROM chat_messages WHERE role = 'user'")
           
           # Active users (last 7 days)
           active_users = await conn.fetchval(
               "SELECT COUNT(DISTINCT user_id) FROM chat_sessions WHERE last_activity > NOW() - INTERVAL '7 days'"
           )
       
       return {
           "positive_feedback_rate": feedback_rate,
           "total_queries": total_queries,
           "active_users_7d": active_users
       }
   ```

### Acceptance Criteria
- [ ] Urdu content searchable and responses generated correctly
- [ ] User preferences saved and applied (e.g., language, difficulty level)
- [ ] Chat history accessible from multiple devices
- [ ] Feedback buttons functional, data stored in database
- [ ] Analytics dashboard shows positive feedback rate >= 75% (SC-007)

---

## Deployment (Production)

### Railway Deployment (Backend)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### GitHub Pages Deployment (Frontend)
```bash
cd book
npm run build
npm run deploy  # Deploys to gh-pages branch
```

### Environment Variables (Production)
```
NEON_CONNECTION_STRING=<production-db-url>
QDRANT_URL=<qdrant-cloud-url>
QDRANT_API_KEY=<qdrant-api-key>
GEMINI_API_KEY=<gemini-api-key>
BETTER_AUTH_URL=<better-auth-service-url>
ADMIN_API_KEY=<secure-random-key>
CORS_ORIGINS=https://physicalai-textbook.com
```

---

## Success Validation

### Functional Requirements (28 FRs)
Run through spec.md checklist:
- [ ] FR-001: Vector search with 0.7 threshold
- [ ] FR-002: Streaming responses (< 500ms first chunk)
- [ ] FR-003-005: Citations, below-threshold handling
- [ ] FR-009-011: Guest access, upgrade prompts, migration
- [ ] FR-016-019: Chat history, retention, authenticated persistence
- [ ] FR-020: Better Auth integration
- [ ] FR-021: Below-threshold logging
- [ ] FR-023: Urdu support
- [ ] (Continue for all 28 FRs)

### Success Criteria (9 SCs)
Run acceptance tests:
- [ ] SC-001: < 2s response time (measure with `time curl ...`)
- [ ] SC-006: 50+ concurrent users (load test with `locust`)
- [ ] SC-007: 75%+ positive feedback (check analytics endpoint)
- [ ] SC-008: Deployment within 7 days (track with calendar)

---

**Status**: Quickstart Complete  
**Next Steps**: Update plan.md with all findings and cross-references  
**Total Estimated Time**: 5-7 days (hackathon-ready)
