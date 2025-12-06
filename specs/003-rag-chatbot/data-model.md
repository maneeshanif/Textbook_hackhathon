# Data Model: RAG Chatbot for Physical AI Textbook

**Feature**: 003-rag-chatbot  
**Date**: 2025-12-06  
**Phase**: Phase 1 (Design)

## Overview

This document defines the data schemas for the RAG chatbot system, including relational database tables (Neon Postgres) and vector store collections (Qdrant Cloud). The design supports guest/authenticated users, 90-day retention for anonymous sessions, and multilingual content (English/Urdu).

---

## 1. Postgres Database Schema

### 1.1 Users Table

Stores authenticated user accounts (bonus feature: Better Auth integration).

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

**Fields:**
- `id`: Unique user identifier (UUID for Better Auth compatibility)
- `email`: User's email address (unique constraint for authentication)
- `name`: Display name (optional, can be updated via Better Auth)
- `email_verified`: Email verification status (managed by Better Auth)
- `image_url`: Profile picture URL (optional)
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update timestamp

**Relationships:**
- One user → many chat sessions
- One user → many feedback ratings

---

### 1.2 Chat Sessions Table

Groups related messages into conversation threads. Supports both anonymous (user_id = NULL) and authenticated sessions.

```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- NULL for anonymous
    session_token VARCHAR(64),  -- For anonymous session tracking (hashed)
    language VARCHAR(5) DEFAULT 'en' CHECK (language IN ('en', 'ur')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id, created_at DESC);
CREATE INDEX idx_chat_sessions_token ON chat_sessions(session_token) WHERE user_id IS NULL;
CREATE INDEX idx_chat_sessions_cleanup ON chat_sessions(created_at) WHERE user_id IS NULL;
```

**Fields:**
- `id`: Unique session identifier
- `user_id`: Foreign key to users table (NULL for guest users)
- `session_token`: Hashed token for anonymous session tracking (browser fingerprint or generated UUID)
- `language`: Interface language preference ('en' or 'ur')
- `created_at`: Session start timestamp
- `last_activity`: Last message timestamp (updated on each query)

**Indexes:**
- `idx_chat_sessions_user`: Fast lookup of user's sessions
- `idx_chat_sessions_token`: Anonymous session lookup by token
- `idx_chat_sessions_cleanup`: Efficient cleanup query for 90-day retention (partial index on anonymous sessions)

**Retention Policy:**
- Anonymous sessions (`user_id IS NULL`): Deleted after 90 days via background job
- Authenticated sessions: Unlimited retention (FR-019)

---

### 1.3 Chat Messages Table

Stores individual messages (user queries and assistant responses) within sessions.

```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',  -- Stores citations, similarity scores, etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at DESC);
```

**Fields:**
- `id`: Unique message identifier
- `session_id`: Foreign key to chat_sessions table
- `role`: Message sender ('user' or 'assistant')
- `content`: Full message text (user query or assistant response)
- `metadata`: JSON field for additional context:
  - `citations`: Array of chapter references (e.g., `["2.1.3", "3.4.1"]`)
  - `similarity_scores`: Top similarity scores from vector search
  - `response_time_ms`: Time taken to generate response
  - `tokens_used`: Token count for cost tracking (optional)
- `created_at`: Message timestamp

**Indexes:**
- `idx_chat_messages_session`: Efficient retrieval of session history in chronological order

**Cascade Behavior:**
- When session is deleted (90-day cleanup), all messages are automatically deleted

---

### 1.4 Feedback Ratings Table

Stores user feedback (thumbs up/down) for assistant responses (FR-018).

```sql
CREATE TABLE feedback_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL CHECK (rating IN (1, -1)),  -- 1 = thumbs up, -1 = thumbs down
    feedback_text TEXT,  -- Optional user comment
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feedback_ratings_message ON feedback_ratings(message_id);
CREATE INDEX idx_feedback_ratings_created ON feedback_ratings(created_at DESC);
```

**Fields:**
- `id`: Unique rating identifier
- `message_id`: Foreign key to chat_messages table (assistant messages only)
- `rating`: 1 for positive, -1 for negative
- `feedback_text`: Optional text feedback from user
- `created_at`: Feedback submission timestamp

**Indexes:**
- `idx_feedback_ratings_message`: Lookup ratings for specific message
- `idx_feedback_ratings_created`: Aggregate ratings over time periods

**Analytics Queries:**
```sql
-- Calculate positive feedback rate (SC-007: target 75%)
SELECT 
    COUNT(*) FILTER (WHERE rating = 1)::FLOAT / COUNT(*) AS positive_rate
FROM feedback_ratings;

-- Identify low-rated responses for improvement
SELECT 
    cm.content AS response,
    cm.metadata->>'citations' AS citations,
    COUNT(*) FILTER (WHERE fr.rating = -1) AS negative_count
FROM chat_messages cm
JOIN feedback_ratings fr ON fr.message_id = cm.id
WHERE cm.role = 'assistant'
GROUP BY cm.id
ORDER BY negative_count DESC
LIMIT 20;
```

---

## 2. Qdrant Vector Store Schema

### 2.1 Collections

Two separate collections for English and Urdu content (FR-023).

```python
# Collection names
COLLECTIONS = {
    "en": "textbook_chunks_en",
    "ur": "textbook_chunks_ur"
}

# Vector dimensions
VECTOR_SIZE = 768  # Gemini text-embedding-004 (default)
```

### 2.2 Collection Configuration

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

async def create_collections():
    for lang, collection_name in COLLECTIONS.items():
        await qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE  # Cosine similarity for semantic search
            )
        )
```

### 2.3 Point Schema

Each vector point represents a chunk of textbook content.

```python
{
    "id": "module-1_week-1-2_intro_chunk_0",  # Unique identifier (chapter + chunk index)
    "vector": [0.123, -0.456, ...],  # 1536-dimensional embedding
    "payload": {
        "text": "Forward kinematics is the process of...",  # Original chunk text
        "chapter": "1.1.2",  # Chapter reference (for citations)
        "section": "Introduction to Robot Kinematics",  # Section title
        "module": "module-1",  # Top-level module
        "week": "week-1-2",  # Week grouping
        "language": "en",  # 'en' or 'ur'
        "file_path": "docs/module-1/week-1-2/index.mdx",  # Source file
        "chunk_index": 0,  # Position within document
        "token_count": 487  # Approx tokens (for chunking validation)
    }
}
```

**Payload Fields:**
- `text`: Full chunk content (used for LLM context)
- `chapter`: Hierarchical chapter reference (e.g., "2.1.3") for citations (FR-005)
- `section`: Human-readable section title for UI display
- `module`, `week`: Hierarchical organization (matches Docusaurus structure)
- `language`: Language code for filtering (FR-023)
- `file_path`: Source file for debugging/re-ingestion
- `chunk_index`: Position within document (for preserving order)
- `token_count`: Approximate token count (metadata only)

### 2.4 Search Filters

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

# Example: Search only English content
language_filter = Filter(
    must=[
        FieldCondition(
            key="language",
            match=MatchValue(value="en")
        )
    ]
)

# Example: Search specific module
module_filter = Filter(
    must=[
        FieldCondition(
            key="module",
            match=MatchValue(value="module-2")
        )
    ]
)

# Example: Hybrid filter (language + module)
hybrid_filter = Filter(
    must=[
        FieldCondition(key="language", match=MatchValue(value="ur")),
        FieldCondition(key="module", match=MatchValue(value="module-1"))
    ]
)
```

---

## 3. Data Relationships

### 3.1 Entity-Relationship Diagram

```
┌──────────────┐
│    users     │
│──────────────│
│ id (PK)      │────┐
│ email        │    │
│ name         │    │
│ ...          │    │
└──────────────┘    │
                    │ 1:N
                    ▼
              ┌──────────────────┐
              │  chat_sessions   │
              │──────────────────│
              │ id (PK)          │────┐
              │ user_id (FK)     │    │
              │ session_token    │    │
              │ language         │    │
              │ ...              │    │
              └──────────────────┘    │
                                      │ 1:N
                                      ▼
                                ┌──────────────────┐
                                │  chat_messages   │
                                │──────────────────│
                                │ id (PK)          │────┐
                                │ session_id (FK)  │    │
                                │ role             │    │
                                │ content          │    │
                                │ metadata         │    │
                                │ ...              │    │
                                └──────────────────┘    │
                                                        │ 1:N
                                                        ▼
                                                  ┌───────────────────┐
                                                  │ feedback_ratings  │
                                                  │───────────────────│
                                                  │ id (PK)           │
                                                  │ message_id (FK)   │
                                                  │ rating            │
                                                  │ feedback_text     │
                                                  │ ...               │
                                                  └───────────────────┘

                    ┌────────────────────────────────┐
                    │  Qdrant Collections (Separate) │
                    │────────────────────────────────│
                    │  textbook_chunks_en            │
                    │  textbook_chunks_ur            │
                    │                                │
                    │  Each point has payload:       │
                    │  - text, chapter, section,     │
                    │    module, week, language      │
                    └────────────────────────────────┘
                              ▲
                              │ Referenced by chat_messages.metadata->>'citations'
                              │ (No direct FK, referenced by chapter string)
```

### 3.2 Data Flow

1. **User Query** → `chat_messages` table (role='user')
2. **Vector Search** → Qdrant collection (filtered by language)
3. **LLM Response** → `chat_messages` table (role='assistant', metadata with citations)
4. **User Feedback** → `feedback_ratings` table (linked to assistant message)

---

## 4. Data Access Patterns

### 4.1 Chat History Retrieval

```sql
-- Get recent chat history for session (for context window)
SELECT role, content, created_at
FROM chat_messages
WHERE session_id = ?
ORDER BY created_at DESC
LIMIT 20;  -- Last 20 messages
```

### 4.2 Anonymous Session Cleanup

```sql
-- Delete anonymous sessions older than 90 days (FR-019)
DELETE FROM chat_sessions
WHERE user_id IS NULL
  AND created_at < NOW() - INTERVAL '90 days'
RETURNING id;

-- Cascade deletion will automatically remove:
-- - Associated chat_messages (via ON DELETE CASCADE)
-- - Associated feedback_ratings (via message ON DELETE CASCADE)
```

### 4.3 Session Migration (Guest → Authenticated)

```sql
-- Update anonymous session to authenticated user (FR-011)
UPDATE chat_sessions
SET user_id = ?, session_token = NULL
WHERE session_token = ? AND user_id IS NULL;
```

### 4.4 Vector Search with Metadata Filtering

```python
# Search English content from Module 2
results = await qdrant_client.search(
    collection_name="textbook_chunks_en",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(key="module", match=MatchValue(value="module-2"))
        ]
    ),
    limit=5,
    score_threshold=0.7  # FR-004: Minimum similarity
)

# Extract citations from results
citations = [hit.payload["chapter"] for hit in results]
```

---

## 5. Storage Estimates

### 5.1 Postgres Database (Neon Free Tier: 512MB)

| Table | Rows (Est.) | Row Size | Total |
|-------|-------------|----------|-------|
| `users` | 500 users | ~200 bytes | 100 KB |
| `chat_sessions` | 2000 sessions | ~150 bytes | 300 KB |
| `chat_messages` | 50,000 messages | ~500 bytes | 25 MB |
| `feedback_ratings` | 10,000 ratings | ~100 bytes | 1 MB |
| **Total** | | | **~27 MB** |

**Headroom**: 485 MB remaining for growth (18x capacity)

### 5.2 Qdrant Cloud (Free Tier: 1GB)

| Collection | Vectors (Est.) | Vector Size | Payload Size | Total |
|------------|----------------|-------------|--------------|-------|
| `textbook_chunks_en` | 400 chunks | 6 KB/vector | 1 KB/chunk | ~2.8 MB |
| `textbook_chunks_ur` | 400 chunks | 6 KB/vector | 1 KB/chunk | ~2.8 MB |
| **Total** | 800 vectors | | | **~5.6 MB** |

**Headroom**: 994 MB remaining (177x capacity)

**Calculation Details:**
- Vector size: 1536 dimensions × 4 bytes (float32) = 6,144 bytes ≈ 6 KB
- Payload size: ~1 KB (text metadata, chapter refs, etc.)
- Estimated 400 chunks per language (4 modules × 10 weeks × 10 chunks/week)

---

## 6. Validation Rules

### 6.1 Postgres Constraints

```sql
-- Enforce valid message roles
CHECK (role IN ('user', 'assistant'))

-- Enforce valid languages
CHECK (language IN ('en', 'ur'))

-- Enforce valid feedback ratings
CHECK (rating IN (1, -1))

-- Prevent negative token counts
CHECK (token_count >= 0)
```

### 6.2 Application-Level Validation

```python
# Message content must not be empty
assert len(message.content.strip()) > 0, "Message content cannot be empty"

# Session token required for anonymous sessions
if session.user_id is None:
    assert session.session_token is not None, "Anonymous sessions must have session_token"

# Feedback can only be submitted for assistant messages
assert message.role == "assistant", "Feedback only allowed for assistant responses"

# Citation chapters must exist in Qdrant payload
for citation in metadata.get("citations", []):
    assert is_valid_chapter(citation), f"Invalid chapter reference: {citation}"
```

---

## 7. Migration Strategy

### 7.1 Initial Schema Migration

```bash
# Run migrations on Neon Postgres
psql $NEON_CONNECTION_STRING < migrations/001_init_schema.sql
```

### 7.2 Qdrant Collection Initialization

```python
# Run once during deployment setup
await create_collections()
print(f"Created collections: {list(COLLECTIONS.values())}")
```

### 7.3 Data Seeding (Ingestion)

```bash
# Ingest MDX files into Qdrant
python scripts/ingest_textbook.py --language en --path book/docs
python scripts/ingest_textbook.py --language ur --path book/i18n/ur/docusaurus-plugin-content-docs/current
```

---

## 8. Backup & Recovery

### 8.1 Postgres Backups (Neon)

- **Automatic**: Neon provides point-in-time recovery (PITR) for free tier
- **Retention**: 7 days of transaction history
- **Recovery**: Via Neon dashboard or CLI

### 8.2 Qdrant Backups (Qdrant Cloud)

- **Snapshots**: Create collection snapshots via API
- **Frequency**: Weekly snapshots during ingestion (idempotent)
- **Recovery**: Re-run ingestion script (deterministic chunk IDs)

```python
# Create Qdrant snapshot
await qdrant_client.create_snapshot(collection_name="textbook_chunks_en")
```

---

##  9. Performance Considerations

### 9.1 Indexing Strategy

**Postgres:**
- Primary indexes on all foreign keys
- Partial index on anonymous sessions for cleanup efficiency
- Covering index on `(session_id, created_at)` for chat history queries

**Qdrant:**
- HNSW index (default) optimized for approximate nearest neighbor search
- `ef_construct=100`, `m=16` for balance between speed and accuracy

### 9.2 Query Optimization

```sql
-- Optimized chat history query (uses index)
EXPLAIN ANALYZE
SELECT role, content, created_at
FROM chat_messages
WHERE session_id = '...'
ORDER BY created_at DESC
LIMIT 20;
-- Expected: Index Scan on idx_chat_messages_session
```

### 9.3 Connection Pooling

```python
# asyncpg pool configuration (see research.md Section 4)
db_pool = await asyncpg.create_pool(
    ...,
    min_size=2,
    max_size=10,
    command_timeout=60
)
```

---

## 10. Security Considerations

### 10.1 Data Encryption

- **At Rest**: Neon and Qdrant Cloud provide automatic encryption
- **In Transit**: All connections use TLS (PostgreSQL SSL mode, Qdrant HTTPS)

### 10.2 Access Control

```python
# Parameterized queries prevent SQL injection
await conn.execute(
    "INSERT INTO chat_messages (session_id, role, content) VALUES ($1, $2, $3)",
    session_id, role, content
)

# Row-level security (optional for production)
CREATE POLICY user_sessions ON chat_sessions
    FOR SELECT
    USING (user_id = current_setting('app.user_id')::UUID OR user_id IS NULL);
```

### 10.3 PII Handling

- **User emails**: Hashed for anonymous analytics (GDPR compliance)
- **Chat content**: Not indexed for search outside vector DB
- **Session tokens**: Hashed with SHA-256 before storage

---

**Status**: Data Model Complete  
**Next Steps**: Generate API contracts (OpenAPI specs for 7 endpoints)  
**Dependencies**: Research findings validated, ready for implementation
