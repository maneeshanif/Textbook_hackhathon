# Research Findings: RAG Chatbot for Physical AI Textbook

**Feature**: 003-rag-chatbot  
**Date**: 2025-12-06  
**Research Phase**: Phase 0

## Executive Summary

This document consolidates research findings for implementing a RAG chatbot embedded in the Physical AI textbook. All technology choices have been validated through Context7 documentation lookups and Microsoft Learn best practices. The recommended stack balances hackathon constraints (rapid development, free tiers) with production-ready patterns (observability, security, scalability).

---

## 1. FastAPI + Qdrant Integration

### Decision
Use FastAPI async patterns with Qdrant Python client for semantic search endpoints.

### Rationale
- **FastAPI**: Native async/await support, automatic OpenAPI docs, streaming responses via `StreamingResponse`
- **Qdrant Client**: High-performance vector search with both sync/async clients, minimal latency overhead
- **Integration Pattern**: Async endpoint → await Qdrant search → stream LLM response

### Implementation Patterns

#### Streaming Response Endpoint
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from qdrant_client import AsyncQdrantClient
import asyncio

app = FastAPI()
qdrant_client = AsyncQdrantClient(url="https://your-qdrant-cloud.qdrant.io")

async def generate_rag_response(query: str):
    # Vector search
    search_results = await qdrant_client.search(
        collection_name="textbook_chunks_en",
        query_vector=await get_embedding(query),
        limit=5
    )
    
    # Stream LLM response with context
    async for chunk in stream_llm_with_context(query, search_results):
        yield f"data: {chunk}\n\n"
        await asyncio.sleep(0.01)  # Prevent overwhelming client

@app.get("/api/chat/query")
async def chat_query(q: str):
    return StreamingResponse(
        generate_rag_response(q),
        media_type="text/event-stream"
    )
```

#### Error Handling Middleware
```python
from fastapi import HTTPException, Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": request.state.request_id  # From middleware
        }
    )

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    import uuid
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response
```

#### Qdrant Vector Search with Filtering
```python
from qdrant_client.models import Filter, FieldCondition, MatchValue
import numpy as np

async def search_with_language_filter(query: str, language: str = "en"):
    query_vector = await get_embedding(query)  # Gemini embedding
    
    hits = await qdrant_client.search(
        collection_name=f"textbook_chunks_{language}",
        query_vector=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="language",
                    match=MatchValue(value=language)
                )
            ]
        ),
        limit=5,
        score_threshold=0.7  # FR-004: Similarity threshold
    )
    
    if not hits:
        return None  # Trigger fallback message
    
    return hits
```

### Key Takeaways
- Use `AsyncQdrantClient` for all async endpoints (required for FastAPI)
- `StreamingResponse` requires async generator or normal iterator
- HTTP exception handlers must return structured errors (no stack traces per FR-012)
- Middleware executes in declaration order (request) and reverse order (response)

---

## 2. Google Gemini Embeddings + Streaming

### Decision
Use `text-embedding-004` for embeddings and `gemini-2.0-flash-exp` for chat with streaming.

### Rationale
- **text-embedding-004**: 768 dimensions (configurable 1-768), free tier 1500 req/day, high quality embeddings for retrieval
- **gemini-2.0-flash-exp**: Fast inference, streaming support, free tier available, multimodal ready
- **Cost**: FREE for hackathon usage (generous free tier: 1500 requests/day, sufficient for 50+ concurrent users)

### Implementation Patterns

#### Embeddings Generation
```python
from google import genai
from google.genai import types
import asyncio

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def get_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model="text-embedding-004",  # 768 dimensions default
        contents=text
    )
    return response.embeddings[0].values

# Batch embedding for ingestion
async def embed_chunks(chunks: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=chunks,
        config=types.EmbedContentConfig(
            task_type='RETRIEVAL_DOCUMENT',  # Optimized for document retrieval
            output_dimensionality=768
        )
    )
    return [emb.values for emb in response.embeddings]
```

#### Streaming Chat Completions
```python
async def stream_llm_with_context(query: str, search_results):
    context = "\n\n".join([hit.payload["text"] for hit in search_results])
    citations = [hit.payload["chapter"] for hit in search_results]
    
    # Stream response with Gemini
    prompt = f"""Answer based on this textbook content:
{context}

Student question: {query}"""
    
    for chunk in client.models.generate_content_stream(
        model="gemini-2.0-flash-exp",
        contents=prompt
    ):
        if chunk.text:
            yield chunk.text
    
    # Append citations after response
    yield f"\n\nSources: {', '.join(citations)}"
```

#### Streaming Pattern
```python
# Simpler streaming pattern with Gemini (no context manager needed)
async def rag_endpoint(query: str):
    for chunk in client.models.generate_content_stream(
        model="gemini-2.0-flash-exp",
        contents=query
    ):
        if chunk.text:
            yield chunk.text
```

### Key Takeaways
- `text-embedding-004` has 768 dimensions by default (50% smaller than OpenAI's 1536)
- Gemini free tier is generous: 1500 requests/day (sufficient for hackathon with 50+ users)
- Streaming uses simpler API: `generate_content_stream()` - no async context managers needed
- Batch embeddings supported with `task_type='RETRIEVAL_DOCUMENT'` optimization
- **Cost-effective: 100% FREE for typical hackathon usage** (< 500 queries/day)

---

## 3. Better Auth Python Integration

### Decision
Use Better Auth with guest/authenticated user flow (FR-009 to FR-011).

### Rationale
- **Session Management**: Better Auth provides JWTokens for stateless auth
- **Guest Support**: LocalStorage on frontend, database migration on signup (FR-011)
- **FastAPI Integration**: Middleware validates `Authorization` header with `auth.api.getSession`

### Implementation Patterns

#### Auth Middleware (FastAPI)
```python
from fastapi import Request, HTTPException
from better_auth_client import BetterAuthClient  # Hypothetical Python client

auth_client = BetterAuthClient(url=os.getenv("BETTER_AUTH_URL"))

async def require_auth(request: Request):
    """Middleware to validate session for protected routes."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        session = await auth_client.get_session(headers=dict(request.headers))
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        request.state.user = session["user"]
        request.state.session = session["session"]
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# Apply to protected routes
@app.post("/api/chat/migrate")
async def migrate_chat_history(request: Request):
    await require_auth(request)
    user_id = request.state.user["id"]
    # Migrate localStorage history from request body to database
    ...
```

#### Guest vs Authenticated Routing
```python
@app.post("/api/chat/query")
async def chat_query(request: Request, query: str):
    # Try to get session (optional for this endpoint)
    session = await auth_client.get_session(headers=dict(request.headers))
    
    if session:
        # Authenticated user: save to database
        user_id = session["user"]["id"]
        await save_message_to_db(user_id, query, response)
    else:
        # Guest user: return response, frontend handles localStorage
        pass
    
    return {"response": response, "is_authenticated": bool(session)}
```

#### Session Migration Endpoint
```python
@app.post("/api/chat/migrate")
async def migrate_history(request: Request, history: list[dict]):
    """Migrate localStorage chat history to database on login (FR-011)."""
    await require_auth(request)
    user_id = request.state.user["id"]
    
    for message in history:
        await db.execute(
            "INSERT INTO chat_messages (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (user_id, message["role"], message["content"], message["timestamp"])
        )
    
    return {"migrated": len(history)}
```

### Key Takeaways
- Better Auth uses JWT tokens in `Authorization: Bearer <token>` header
- Middleware pattern: extract session → attach to `request.state` → access in endpoint
- Guest users: return data, let frontend handle localStorage (no DB writes)
- Authentication triggers upgrade prompt after 5 messages (FR-010 - handled in frontend)

### Note on Python Client
Better Auth is primarily TypeScript/JavaScript. For Python backend:
- **Option A**: Use Better Auth REST API directly (recommended for hackathon)
- **Option B**: Implement simple JWT validation with PyJWT library
- **Option C**: Use Better Auth TypeScript server with Python client calls

**Recommended**: Option A (REST API) for fastest integration during hackathon.

---

## 4. Neon Serverless Postgres with FastAPI

### Decision
Use `asyncpg` with connection pooling for Neon Serverless Postgres.

### Rationale
- **asyncpg**: Fastest async PostgreSQL driver for Python (3-5x faster than psycopg3)
- **Connection Pooling**: Essential for serverless (Neon charges per active connection)
- **Neon Compatibility**: Full PostgreSQL compatibility, auto-scaling, free tier (512MB)

### Implementation Patterns

#### Connection Pool Setup
```python
import asyncpg
import os

# Global connection pool (initialize on startup)
db_pool = None

async def create_db_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(
        host=os.getenv("NEON_HOST"),
        port=5432,
        database=os.getenv("NEON_DATABASE", "main"),
        user=os.getenv("NEON_USER"),
        password=os.getenv("NEON_PASSWORD"),
        min_size=2,
        max_size=10,
        command_timeout=60
    )
    return db_pool

async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()

# FastAPI lifespan events
@app.on_event("startup")
async def startup():
    await create_db_pool()

@app.on_event("shutdown")
async def shutdown():
    await close_db_pool()
```

#### Database Operations
```python
async def save_chat_message(user_id: str, role: str, content: str):
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO chat_messages (user_id, role, content, created_at)
            VALUES ($1, $2, $3, NOW())
            """,
            user_id, role, content
        )

async def get_chat_history(user_id: str, limit: int = 20):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT role, content, created_at
            FROM chat_messages
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            user_id, limit
        )
        return [dict(row) for row in rows]

async def cleanup_old_anonymous_sessions():
    """Background job: delete anonymous sessions older than 90 days (FR-019)."""
    async with db_pool.acquire() as conn:
        deleted = await conn.execute(
            """
            DELETE FROM chat_sessions
            WHERE user_id IS NULL  -- Anonymous sessions
            AND created_at < NOW() - INTERVAL '90 days'
            """
        )
        return deleted
```

#### Schema Migrations
```python
# migrations/001_init_schema.sql
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- NULL for anonymous
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at DESC);
CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id, created_at DESC);
CREATE INDEX idx_chat_sessions_cleanup ON chat_sessions(created_at) WHERE user_id IS NULL;

# Run migrations
async def run_migrations():
    async with db_pool.acquire() as conn:
        with open("migrations/001_init_schema.sql") as f:
            await conn.execute(f.read())
```

### Key Takeaways
- Use `asyncpg.create_pool()` with `min_size=2, max_size=10` for Neon free tier
- ALWAYS use `async with db_pool.acquire()` for connection safety
- Parameterized queries with `$1, $2` prevent SQL injection (FR-005 security)
- Background job for 90-day cleanup (schedule with APScheduler or cron)

---

## 5. React Chat Widget in Docusaurus

### Decision
Create swizzled React component integrated into Docusaurus theme.

### Rationale
- **Docusaurus Swizzling**: Allows custom components in theme without ejecting
- **React Hooks**: `useState` for chat state, `useEffect` for text selection listener
- **localStorage**: Persist anonymous sessions (FR-009), migrate on auth (FR-011)

### Implementation Patterns

#### Chat Widget Component
```tsx
// book/src/components/ChatWidget/index.tsx
import React, { useState, useEffect } from 'react';
import styles from './styles.module.css';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState(() => {
    // Load from localStorage for anonymous users
    const saved = localStorage.getItem('chat_history');
    return saved ? JSON.parse(saved) : [];
  });
  const [input, setInput] = useState('');
  const [selectedText, setSelectedText] = useState('');

  // Save to localStorage on message change
  useEffect(() => {
    localStorage.setItem('chat_history', JSON.stringify(messages));
  }, [messages]);

  // Text selection handler
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection()?.toString();
      if (selection && selection.length > 0) {
        setSelectedText(selection);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  const sendMessage = async () => {
    const query = selectedText ? `${input}\n\nContext: ${selectedText}` : input;
    setMessages([...messages, { role: 'user', content: input }]);

    const response = await fetch('/api/chat/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });

    const reader = response.body.getReader();
    let assistantMessage = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = new TextDecoder().decode(value);
      assistantMessage += chunk;
      // Update UI with streaming response
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: 'assistant', content: assistantMessage };
        return updated;
      });
    }

    setSelectedText(''); // Clear selection after use
  };

  return (
    <div className={styles.chatWidget}>
      <button onClick={() => setIsOpen(!isOpen)}>💬 Ask AI</button>
      {isOpen && (
        <div className={styles.chatWindow}>
          {/* Chat UI */}
        </div>
      )}
    </div>
  );
}
```

#### Docusaurus Integration
```tsx
// book/src/theme/Root.tsx (swizzled)
import React from 'react';
import ChatWidget from '@site/src/components/ChatWidget';

export default function Root({ children }) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
```

#### Auth Upgrade Prompt
```tsx
// After 5 messages (FR-010)
useEffect(() => {
  if (messages.filter(m => m.role === 'user').length === 5 && !isAuthenticated) {
    setShowUpgradePrompt(true);
  }
}, [messages]);

const UpgradePrompt = () => (
  <div className={styles.prompt}>
    <h3>Unlock Unlimited Chat</h3>
    <ul>
      <li>✅ Unlimited message history</li>
      <li>✅ Cross-device sync</li>
      <li>✅ Personalized responses</li>
    </ul>
    <button onClick={() => window.location.href = '/auth/signup'}>
      Sign Up Free
    </button>
  </div>
);
```

### Key Takeaways
- Swizzle `Root.tsx` to inject widget globally
- Use `window.getSelection()` API for text selection (FR-006)
- localStorage key: `chat_history` (array of `{role, content, timestamp}`)
- Stream response with `ReadableStream` API for real-time updates (FR-007)

---

## 6. MDX Content Ingestion Pipeline

### Decision
Use `unified` + `remark` for MDX parsing, exclude code blocks, chunk with overlap.

### Rationale
- **unified/remark**: Industry-standard MDX AST parser
- **Code Exclusion** (FR-017): Code explanations in prose are more semantically meaningful
- **Chunking Strategy**: 500 tokens per chunk, 50-token overlap prevents context loss at boundaries

### Implementation Patterns

#### MDX Parsing
```python
# ingestion/parse_mdx.py
import subprocess
import json

def parse_mdx_to_text(mdx_file_path: str) -> str:
    """Parse MDX file and extract plain text (no code blocks)."""
    # Use Node.js script with unified/remark
    result = subprocess.run(
        ['node', 'scripts/mdx-parser.js', mdx_file_path],
        capture_output=True,
        text=True
    )
    return result.stdout

# scripts/mdx-parser.js
const fs = require('fs');
const unified = require('unified');
const remarkParse = require('remark-parse');
const remarkMdx = require('remark-mdx');
const remarkStringify = require('remark-stringify');
const visit = require('unist-util-visit');

const mdxFilePath = process.argv[2];
const mdxContent = fs.readFileSync(mdxFilePath, 'utf8');

const processor = unified()
  .use(remarkParse)
  .use(remarkMdx)
  .use(() => (tree) => {
    // Remove code blocks
    visit(tree, 'code', (node, index, parent) => {
      parent.children.splice(index, 1);
    });
  })
  .use(remarkStringify);

const result = processor.processSync(mdxContent);
console.log(result.toString());
```

#### Semantic Chunking
```python
import tiktoken

def chunk_text_with_overlap(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Chunk text into ~500 token segments with 50-token overlap."""
    # Note: Gemini has its own tokenization, but for compatibility:
    encoder = tiktoken.encoding_for_model("gpt-4")  # Approximate for token counting
    tokens = encoder.encode(text)
    
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(encoder.decode(chunk_tokens))
        start += (chunk_size - overlap)  # Step back for overlap
    
    return chunks

async def ingest_mdx_file(mdx_path: str, metadata: dict):
    """Full ingestion pipeline for one MDX file."""
    # 1. Parse MDX to plain text
    text = parse_mdx_to_text(mdx_path)
    
    # 2. Chunk text
    chunks = chunk_text_with_overlap(text)
    
    # 3. Generate embeddings
    embeddings = await embed_chunks(chunks)
    
    # 4. Upload to Qdrant
    points = [
        {
            "id": f"{metadata['chapter']}_{i}",
            "vector": embedding,
            "payload": {
                "text": chunk,
                "chapter": metadata["chapter"],
                "section": metadata["section"],
                "language": metadata["language"]
            }
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    
    await qdrant_client.upsert(
        collection_name=f"textbook_chunks_{metadata['language']}",
        points=points
    )
```

### Key Takeaways
- Use Node.js script for MDX parsing (remark ecosystem is JS-native)
- Python handles embedding + Qdrant upload (async I/O advantage)
- 500 tokens ≈ 375 words (safe for context windows)
- 50-token overlap prevents semantic breaks at chunk boundaries

---

## 7. Structured Logging with FastAPI

### Decision
Use Python `logging` module with JSON formatter + FastAPI middleware for request tracing.

### Rationale
- **Standard Library**: No external dependencies (`structlog` adds complexity for hackathon)
- **JSON Output**: Queryable logs for debugging (vs plain text)
- **Request IDs**: Trace full request lifecycle (FR-026, FR-028)

### Implementation Patterns

#### Logging Configuration
```python
import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "query_text"):
            log_data["query_text"] = record.query_text
        if hasattr(record, "response_time_ms"):
            log_data["response_time_ms"] = record.response_time_ms
        
        return json.dumps(log_data)

# Configure root logger
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

logger = logging.getLogger("rag_chatbot")
```

#### Request Tracing Middleware
```python
import time
import uuid
from fastapi import Request

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host
        }
    )
    
    try:
        response = await call_next(request)
        response_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "response_time_ms": round(response_time_ms, 2)
            }
        )
        
        response.headers["X-Request-ID"] = request_id
        return response
    
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "response_time_ms": round(response_time_ms, 2)
            },
            exc_info=True
        )
        raise
```

#### Query-Specific Logging
```python
@app.post("/api/chat/query")
async def chat_query(request: Request, query: str):
    # Log query with request ID
    logger.info(
        "Query received",
        extra={
            "request_id": request.state.request_id,
            "query_text": query[:100],  # Truncate for privacy
            "user_id": getattr(request.state, "user", {}).get("id")
        }
    )
    
    # Vector search
    search_results = await search_with_language_filter(query)
    
    if not search_results:
        # Log below-threshold query (FR-021)
        logger.warning(
            "Query below similarity threshold",
            extra={
                "request_id": request.state.request_id,
                "query_text": query,
                "threshold": 0.7
            }
        )
        return {"error": "No relevant content found"}
    
    # Log retrieval quality
    logger.info(
        "Vector search completed",
        extra={
            "request_id": request.state.request_id,
            "num_results": len(search_results),
            "top_score": search_results[0].score,
            "avg_score": sum(r.score for r in search_results) / len(search_results)
        }
    )
    
    return await generate_response(query, search_results)
```

### Key Takeaways
- JSON logs go to stdout (Docker-friendly, captured by container orchestration)
- Request ID propagated through `request.state` (accessible in all route handlers)
- Log query text for debugging but truncate/hash for production privacy
- Track metrics: response_time_ms, similarity scores, error types (FR-027)

---

## 8. Vector Search Quality Metrics

### Decision
Track similarity scores, latency percentiles, and below-threshold queries in-memory (no APM tool).

### Rationale
- **Hackathon Constraint**: Avoid external dependencies (Prometheus, Grafana)
- **In-Memory Metrics**: Sufficient for demo week, export to `/metrics` endpoint
- **Quality Signal**: Below-threshold queries identify content gaps (FR-021)

### Implementation Patterns

#### Metrics Collection
```python
from collections import defaultdict, deque
import time

class MetricsCollector:
    def __init__(self, window_size=1000):
        self.query_count = 0
        self.error_count_by_type = defaultdict(int)
        self.latency_samples = deque(maxlen=window_size)  # Last 1000 requests
        self.similarity_scores = deque(maxlen=window_size)
        self.below_threshold_queries = []
    
    def record_query(self, latency_ms: float, top_score: float, query: str = None):
        self.query_count += 1
        self.latency_samples.append(latency_ms)
        self.similarity_scores.append(top_score)
        
        if top_score < 0.7 and query:
            self.below_threshold_queries.append({
                "query": query,
                "score": top_score,
                "timestamp": time.time()
            })
    
    def record_error(self, error_type: str):
        self.error_count_by_type[error_type] += 1
    
    def get_percentile(self, samples: list, percentile: float) -> float:
        if not samples:
            return 0.0
        sorted_samples = sorted(samples)
        index = int(len(sorted_samples) * (percentile / 100))
        return sorted_samples[index]
    
    def get_metrics(self) -> dict:
        return {
            "query_volume": self.query_count,
            "error_rates": dict(self.error_count_by_type),
            "latency_p50": self.get_percentile(list(self.latency_samples), 50),
            "latency_p95": self.get_percentile(list(self.latency_samples), 95),
            "latency_p99": self.get_percentile(list(self.latency_samples), 99),
            "avg_similarity": sum(self.similarity_scores) / len(self.similarity_scores) if self.similarity_scores else 0,
            "below_threshold_count": len(self.below_threshold_queries),
            "below_threshold_rate": len(self.below_threshold_queries) / self.query_count if self.query_count > 0 else 0
        }

metrics = MetricsCollector()
```

#### Metrics Endpoint
```python
@app.get("/api/metrics")
async def get_metrics():
    """Expose operational metrics (FR-027)."""
    return metrics.get_metrics()

@app.get("/api/metrics/low-quality-queries")
async def get_low_quality_queries(limit: int = 50):
    """Retrieve queries below similarity threshold for content gap analysis."""
    return {
        "queries": metrics.below_threshold_queries[-limit:],
        "total": len(metrics.below_threshold_queries)
    }
```

#### Integration with Endpoints
```python
@app.post("/api/chat/query")
async def chat_query(request: Request, query: str):
    start_time = time.time()
    
    try:
        search_results = await search_with_language_filter(query)
        
        if not search_results:
            metrics.record_query(
                latency_ms=(time.time() - start_time) * 1000,
                top_score=0.0,
                query=query
            )
            return {"error": "No relevant content found"}
        
        response = await generate_response(query, search_results)
        
        latency_ms = (time.time() - start_time) * 1000
        metrics.record_query(
            latency_ms=latency_ms,
            top_score=search_results[0].score
        )
        
        return response
    
    except Exception as e:
        metrics.record_error(type(e).__name__)
        raise
```

### Key Takeaways
- Use `deque(maxlen=N)` for fixed-size rolling windows (memory-efficient)
- Export `/metrics` endpoint for observability without heavy APM tools
- Track below-threshold queries for content improvement iterations
- Percentile calculation: sort samples, index at `len * (p/100)`

---

## Technology Stack Summary

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Backend Framework** | FastAPI | Async/await, OpenAPI docs, streaming support |
| **Vector Database** | Qdrant Cloud | Free tier 1GB, async client, high performance |
| **Embeddings** | Google Gemini `text-embedding-004` | Free tier, 768 dims, optimized for retrieval |
| **LLM** | Google Gemini `gemini-2.0-flash-exp` | Fast inference, streaming, free tier |
| **Database** | Neon Serverless Postgres | Free tier 512MB, auto-scaling, asyncpg support |
| **Auth** | Better Auth (REST API) | JWT sessions, guest support, easy integration |
| **Frontend** | React (Docusaurus swizzled) | Existing infrastructure, localStorage, streaming |
| **Logging** | Python `logging` + JSON | Structured logs, request tracing, no dependencies |
| **Metrics** | In-memory collector | Hackathon-friendly, exportable via REST endpoint |

---

## Deployment Architecture

```
┌─────────────────┐
│  GitHub Pages   │ ← Docusaurus static site + React chat widget
│  (Frontend)     │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Railway/Render │ ← FastAPI backend (Docker container)
│  (Backend API)  │
└────┬───────┬────┘
     │       │
     │       └──────────────────┐
     │                          │
     ▼                          ▼
┌─────────────┐        ┌──────────────────┐
│ Qdrant Cloud│        │ Neon Serverless  │
│ (Vectors)   │        │ (Postgres)       │
└─────────────┘        └──────────────────┘
     │
     │ Embeddings API
     ▼
┌─────────────┐
│ Gemini API  │
│ (2.0-flash +│
│  embedding) │
└─────────────┘
```

---

## Next Steps (Phase 1)

1. **Generate data-model.md**: Define Postgres schemas + Qdrant collections
2. **Generate contracts/**: OpenAPI specs for all 7 endpoints
3. **Generate quickstart.md**: Implementation sequence (8 phases)
4. **Update plan.md**: Fill template with research findings
5. **Suggest ADRs**: Document architecture decisions (vector DB choice, embedding model, auth strategy, schema design)

---

**Status**: Research Complete  
**Validation**: All technology choices verified via Context7 + Microsoft Learn  
**Ready for**: Phase 1 (Design & Contracts)
