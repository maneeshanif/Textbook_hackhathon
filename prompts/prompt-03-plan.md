# /sp.plan - Implementation Planning Command

Follow instructions in `.github/prompts/sp.plan.prompt.md`

---

## Feature Context

**Feature**: 003-rag-chatbot  
**Spec**: `specs/003-rag-chatbot/spec.md`  
**Branch**: `003-rag-chatbot`

## Technical Context (Pre-filled from Project Constitution & Spec Clarifications)

Based on requirements.md, spec.md, and clarification decisions:

**Language/Version**: Python 3.11+ (backend), TypeScript/React (frontend widget)  
**Primary Dependencies**: 
  - Backend: FastAPI, Qdrant Python client, OpenAI SDK, Better Auth Python client, Neon Serverless Postgres driver
  - Frontend: React 18, TypeScript, Docusaurus React components
**Storage**: 
  - Vector DB: Qdrant Cloud (embeddings, semantic search)
  - Relational: Neon Serverless Postgres (chat history, user accounts)
  - Cache: Browser localStorage (anonymous sessions)
**Testing**: pytest (backend unit/integration), Jest + React Testing Library (frontend), Playwright (E2E)  
**Target Platform**: 
  - Backend: Docker container (FastAPI server)
  - Frontend: Web widget embedded in Docusaurus pages
  - Deployment: Vercel/Railway (backend), GitHub Pages (frontend)
**Project Type**: Full-stack AI application (RAG system)  
**Performance Goals**: 
  - <3s query response time (p95)
  - <500ms widget load time
  - 50+ concurrent users without degradation
**Constraints**: 
  - Hackathon timeline (rapid development)
  - Free tier limits: Qdrant Cloud (1GB), Neon (512MB), OpenAI (rate limits)
  - 0.7 similarity threshold for retrieval quality
  - 90-day retention for anonymous sessions
**Scale/Scope**: 
  - ~200 pages of textbook content to embed
  - 4 modules × 2 languages = ~400 vector chunks
  - Estimated 100-500 users during demo week
  - 28 functional requirements (4 bonus features)

## Constitution Gates to Verify

From `.specify/memory/constitution.md` and `.github/copilot-instructions.md`:

1. ✅ **Context7-First**: Fetch docs for FastAPI, Qdrant, OpenAI, Better Auth, Neon before coding
2. ✅ **Subagent Delegation**: Route to `rag-service` agent (backend) and `ui-embed` agent (frontend)
3. ✅ **Skills Library**: Use `rag-chatbot`, `auth-personalization`, and `ui-embed` skills
4. ✅ **TDD**: pytest for API endpoints, Jest for React components, E2E for chat flow
5. ✅ **Security**: API keys in .env, rate limiting, input sanitization (prompt injection defense)
6. ✅ **Smallest Diff**: MVP first (P1 basic Q&A), then P2-P4 features incrementally
7. ✅ **Docs as Code**: API documentation (OpenAPI), README for setup
8. ✅ **Definition of Done**: All 28 FRs must have acceptance tests
9. ✅ **Better Auth Integration**: Required for +50 bonus points
10. ✅ **Urdu Support**: Required for +50 bonus points (use existing i18n infrastructure)
11. ✅ **Observability**: Structured JSON logs, request tracing, metrics tracking per clarifications
12. ✅ **Quality Control**: 0.7 similarity threshold with fallback messaging per clarifications

## Phase 0: Research Topics

Research needed before implementation planning:

### 1. FastAPI + Qdrant Integration
- **Query**: How to integrate Qdrant vector database with FastAPI for semantic search?
- **Tools**: Context7 lookup for `fastapi` and `qdrant-client`
- **Goal**: Understand async API patterns, connection pooling, error handling
- **Deliverable**: Code snippets for vector search endpoint

### 2. OpenAI Embeddings + Streaming
- **Query**: How to generate embeddings with OpenAI and stream chat completions in FastAPI?
- **Tools**: Context7 lookup for `openai` Python SDK
- **Goal**: Embedding model selection (text-embedding-3-small vs ada-002), streaming response patterns
- **Deliverable**: Sample code for embed + stream endpoints

### 3. Better Auth Python Integration
- **Query**: How to integrate Better Auth with FastAPI backend for guest/authenticated user flow?
- **Tools**: Context7 lookup for `better-auth`, Microsoft Docs search for authentication patterns
- **Goal**: Session management, JWT validation, user migration from localStorage
- **Deliverable**: Auth middleware + user context extraction

### 4. Neon Serverless Postgres with FastAPI
- **Query**: How to connect Neon Postgres to FastAPI with connection pooling?
- **Tools**: Context7 lookup for `psycopg3` or `asyncpg`, Neon documentation
- **Goal**: Async database queries, schema migrations, chat history CRUD
- **Deliverable**: Database connection setup + SQLAlchemy/raw SQL patterns

### 5. React Chat Widget in Docusaurus
- **Query**: How to create embeddable React chat widget that works in Docusaurus MDX pages?
- **Tools**: Context7 lookup for `docusaurus`, React component patterns
- **Goal**: Widget lifecycle (open/close), text selection API, localStorage persistence
- **Deliverable**: Component structure + Docusaurus integration guide

### 6. MDX Content Ingestion Pipeline
- **Query**: How to parse MDX files, chunk content, and generate embeddings for vector DB?
- **Tools**: Context7 for `unified`, `remark`, `mdast` libraries
- **Goal**: Extract text from MDX (exclude code blocks per FR-017), semantic chunking with overlap
- **Deliverable**: Ingestion script architecture

### 7. Structured Logging with FastAPI
- **Query**: How to implement structured JSON logging with request tracing in FastAPI?
- **Tools**: Context7 for `structlog`, Microsoft Docs for logging best practices
- **Goal**: Middleware for request ID generation, log formatting, performance overhead
- **Deliverable**: Logging middleware + configuration

### 8. Vector Search Quality Metrics
- **Query**: How to compute and track similarity scores, latency percentiles, and retrieval quality?
- **Tools**: FastAPI metrics patterns, Prometheus client library (optional)
- **Goal**: Implement FR-027 metrics tracking without heavy APM tools
- **Deliverable**: Metrics collection strategy

## Phase 1: Design Outputs Expected

After research completion, generate these artifacts:

### 1. Architecture Decision Records (ADRs)
Document significant decisions made during research:
- ADR: Vector database choice (Qdrant vs alternatives)
- ADR: Embedding model selection (OpenAI vs open-source)
- ADR: Frontend state management (Context API vs localStorage sync)
- ADR: Database schema design (chat sessions, messages, users)

### 2. Data Model (`specs/003-rag-chatbot/data-model.md`)
Database schemas + vector store structure:
- **Postgres Tables**: users, chat_sessions, chat_messages, feedback_ratings
- **Qdrant Collections**: textbook_chunks_en, textbook_chunks_ur
- **Vector Schema**: chunk_text, embedding, metadata (chapter, section, language)
- **Relationships**: user → sessions → messages

### 3. API Contracts (`specs/003-rag-chatbot/contracts/`)
OpenAPI/JSON schemas for all endpoints:
- `POST /api/chat/query` - Submit question, get streamed response
- `POST /api/chat/query-selection` - Query with selected text context
- `GET /api/chat/history` - Retrieve user's chat history
- `POST /api/chat/migrate` - Migrate localStorage to database on auth
- `POST /api/chat/feedback` - Submit thumbs up/down rating
- `POST /api/admin/ingest` - Trigger content re-embedding
- `GET /api/health` - Health check endpoint

### 4. Component Breakdown (`specs/003-rag-chatbot/quickstart.md`)
Implementation sequence with dependencies:
1. **Backend Foundation** (no frontend deps)
   - FastAPI server scaffold + health endpoint
   - Database connection + schema migrations
   - Structured logging middleware
2. **Ingestion Pipeline** (prerequisite for chat)
   - MDX parser + chunker
   - OpenAI embeddings generation
   - Qdrant upload script
3. **Core RAG Endpoint** (depends on ingestion)
   - Vector search implementation
   - OpenAI chat completion with context
   - Similarity threshold enforcement (FR-004)
   - Streaming response
4. **Chat History API** (depends on database)
   - CRUD operations for messages/sessions
   - Anonymous session management (localStorage sync)
   - 90-day retention cleanup job
5. **Authentication Integration** (Better Auth)
   - Auth middleware + JWT validation
   - Session migration endpoint (FR-011)
   - Guest → authenticated upgrade flow
6. **Frontend Widget** (depends on chat API)
   - React component scaffold
   - Text selection handling
   - localStorage persistence
   - Authentication upgrade prompt (after 5 messages)
7. **Observability & Metrics** (cross-cutting)
   - Request tracing
   - Metrics endpoints
   - Below-threshold query logging (FR-021)
8. **Bonus Features** (after MVP)
   - Urdu language support (FR-023)
   - Personalization (FR-025)
   - Cross-device sync (FR-024)

### 5. Test Strategy
Per TDD constitution requirements:
- **Unit Tests**: pytest for each API endpoint, Jest for React components
- **Integration Tests**: Full RAG flow (query → retrieval → generation → response)
- **E2E Tests**: Playwright for user journeys (guest chat, auth upgrade, selection query)
- **Quality Tests**: Verify 0.7 similarity threshold, fallback messaging, citation accuracy

### 6. Deployment Strategy
Hackathon-optimized deployment:
- **Backend**: Docker container → Railway/Render free tier
- **Frontend**: Docusaurus build → GitHub Pages (existing)
- **Database**: Neon Serverless Postgres (free tier 512MB)
- **Vector DB**: Qdrant Cloud (free tier 1GB)
- **Secrets**: Environment variables via platform UI
- **CI/CD**: GitHub Actions for linting + tests (optional for hackathon)

## Phase 2: Task Breakdown

**NOT generated by /sp.plan** - Use `/sp.tasks` command after plan approval to create:
- `specs/003-rag-chatbot/tasks.md` with red-green-refactor cycles
- Each task with acceptance criteria from functional requirements
- Dependency sequencing based on quickstart.md component breakdown

## Execution Workflow

1. **Run /sp.plan**: Generate research.md, data-model.md, contracts/, quickstart.md in `specs/003-rag-chatbot/`
2. **Review & Approve**: Verify research findings, architecture decisions, API contracts
3. **Create ADRs**: Document significant decisions in `history/adr/`
4. **Run /sp.tasks**: Generate task breakdown with test cases
5. **Begin Implementation**: Follow tasks.md sequence, create PHRs per task

## Expected Deliverables from /sp.plan Command

When user runs `/sp.plan` for this feature:

✅ `specs/003-rag-chatbot/research.md` - Research findings for all 8 topics above  
✅ `specs/003-rag-chatbot/data-model.md` - Database + vector store schemas  
✅ `specs/003-rag-chatbot/contracts/` - OpenAPI specs for all 7 endpoints  
✅ `specs/003-rag-chatbot/quickstart.md` - Implementation sequence (8 phases)  
✅ Updated `specs/003-rag-chatbot/plan.md` - This file with all sections filled  
✅ Suggest 4 ADRs for architecture decisions  

**Do NOT generate**: tasks.md (that's `/sp.tasks` phase)

---

**Status**: Ready for /sp.plan execution  
**Created**: 2025-12-06  
**Spec Clarifications**: 4 questions resolved (retention, auth, observability, vector quality)
