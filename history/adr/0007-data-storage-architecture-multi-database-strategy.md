# ADR-0007: Data Storage Architecture - Multi-Database Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-06
- **Feature:** 003-rag-chatbot
- **Context:** RAG chatbot requires two fundamentally different data models: (1) relational data (users, sessions, messages, feedback) with ACID guarantees and complex queries, and (2) vector embeddings (800 textbook chunks × 768 dimensions) with similarity search. Free tier constraints require careful capacity planning: Neon Postgres 512MB, Qdrant Cloud 1GB. Anonymous users need localStorage → database migration on authentication. 90-day retention policy for anonymous sessions requires efficient cleanup.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use a multi-database strategy with three storage layers:

- **Relational DB**: Neon Serverless Postgres (512MB free tier) for structured data
  - Tables: users, chat_sessions, chat_messages, feedback_ratings
  - Driver: asyncpg 0.29+ (3-5x faster than psycopg3 for async)
  - Connection pooling: min_size=2, max_size=10
  - Usage: ~27 MB (18x headroom on free tier)
- **Vector DB**: Qdrant Cloud (1GB free tier) for semantic search
  - Collections: textbook_chunks_en (400 chunks), textbook_chunks_ur (400 chunks)
  - Dimensions: 768 (Gemini text-embedding-004)
  - Distance: Cosine similarity with HNSW index
  - Usage: ~3.2 MB (311x headroom on free tier)
- **Client Storage**: Browser localStorage for anonymous sessions (pre-auth)
  - Format: JSON array of messages with session_token
  - Migration: Transfer to Postgres on authentication via `/api/chat/migrate`
  - Retention: Browser-managed (cleared on storage quota or user action)

## Consequences

### Positive

- Right tool for each job: relational for ACID, vector for similarity, localStorage for offline-first UX
- Neon serverless driver handles connection lifecycle automatically (no manual pool management)
- asyncpg performance: 3-5x faster than psycopg3 for concurrent async workloads
- Qdrant HNSW index optimized for approximate nearest neighbor (< 100ms search on 800 chunks)
- localStorage enables instant guest access (no signup barrier)
- Free tier headroom: 18x (Postgres) and 311x (Qdrant) - very safe margins
- Independent scaling: can upgrade Postgres without affecting Qdrant (and vice versa)
- Separation of concerns: schema changes don't impact vector search

### Negative

- Three storage systems increase operational complexity (monitoring 3 dashboards)
- localStorage migration logic required (edge cases: partial sync failures, duplicate detection)
- No distributed transactions: session migration is eventually consistent (acceptable for chat history)
- Qdrant Cloud vendor lock-in: migrating 800 vectors to another provider requires full re-ingestion
- Free tier limits create hard capacity constraints (need monitoring alerts at 80%)
- Multi-database joins impossible: must fetch from both and join in application code (performance hit)

## Alternatives Considered

**Alternative A: Postgres with pgvector Extension (Single Database)**
- Pros: Single database, simpler ops, ACID transactions across all data, no vendor lock-in
- Cons: Poor vector search performance (HNSW not as optimized as Qdrant), free tier too small for both relational + vectors (~530 MB total vs 512 MB limit), pg_vector still immature compared to dedicated vector DBs
- Rejected: Storage capacity exceeded, worse search performance, immature vector indexing

**Alternative B: MongoDB with Vector Search (Atlas Free Tier)**
- Pros: Single database (NoSQL), native vector search, 512MB free tier
- Cons: No ACID for complex queries, weaker Python async support, less familiar to team, vector search still beta, difficult schema migrations
- Rejected: Relational model better fit for users/sessions/messages, ACID guarantees important

**Alternative C: Supabase (Postgres + pgvector + Storage)**
- Pros: Integrated platform, generous free tier (500MB DB + 1GB storage), built-in auth, good DX
- Cons: Postgres vector search slower than Qdrant, fewer vector index options, platform lock-in (harder to migrate off)
- Rejected: Vector search performance critical, want flexibility to swap vector DB later

**Why Multi-Database Won**: Best performance for each workload + generous free tier headroom + operational simplicity outweighs coordination complexity.

## References

- Feature Spec: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md)
- Implementation Plan: [specs/003-rag-chatbot/plan.md](../../specs/003-rag-chatbot/plan.md)
- Data Model: [specs/003-rag-chatbot/data-model.md](../../specs/003-rag-chatbot/data-model.md)
- Related ADRs: ADR-0006 (AI Service - determines vector dimensions), ADR-0008 (Auth Strategy - impacts session storage)
