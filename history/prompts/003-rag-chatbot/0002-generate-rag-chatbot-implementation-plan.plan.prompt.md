---
id: 0002
title: "Generate RAG Chatbot Implementation Plan"
stage: plan
date: 2025-12-06
surface: agent
model: claude-sonnet-4.5
feature: 003-rag-chatbot
branch: 003-rag-chatbot
user: maneeshanif
command: /sp.plan
labels: ["planning", "architecture", "rag", "fastapi", "qdrant", "openai", "research"]
links:
  spec: specs/003-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-rag-chatbot/research.md
  - specs/003-rag-chatbot/data-model.md
  - specs/003-rag-chatbot/quickstart.md
  - specs/003-rag-chatbot/contracts/openapi-spec.yaml
  - specs/003-rag-chatbot/contracts/README.md
  - specs/003-rag-chatbot/plan.md
  - .github/copilot-instructions.md
tests:
  - None (planning phase - no code tests)
---

## Prompt

Follow instructions in sp.plan.prompt.md

## Response snapshot

**Phase 0: Research (Completed)**
Fetched authoritative documentation via Context7 for:
- FastAPI (3000 tokens): async API, streaming responses, middleware, error handling
- Qdrant (2000 tokens): vector search, async client, similarity thresholds, filtering
- OpenAI (2000 tokens): embeddings (text-embedding-3-small), streaming chat completions (gpt-4o)
- Better Auth (2000 tokens): session management, JWT validation, guest/auth routing

Supplemented with Microsoft Learn code samples:
- PostgreSQL asyncpg connection pooling (15 samples)
- Structured logging with Python (18 samples)

Generated comprehensive research.md (24KB) with 8 detailed topics:
1. FastAPI + Qdrant integration patterns
2. OpenAI embeddings + streaming implementation
3. Better Auth Python integration (REST API approach)
4. Neon Postgres with asyncpg (3-5x faster than psycopg3)
5. React chat widget in Docusaurus (swizzling)
6. MDX content ingestion pipeline (unified/remark)
7. Structured logging with FastAPI middleware
8. Vector search quality metrics (in-memory collector)

**Phase 1: Design & Contracts (Completed)**
Generated data-model.md with complete schemas:
- 4 Postgres tables: users, chat_sessions, chat_messages, feedback_ratings
- 2 Qdrant collections: textbook_chunks_en, textbook_chunks_ur
- Entity relationships with cascade deletion for 90-day retention
- Storage estimates: Postgres 27 MB (18x headroom), Qdrant 5.6 MB (177x headroom)
- Performance indexes and security considerations

Generated API contracts:
- OpenAPI 3.1 spec with 7 endpoints (chat operations + admin)
- Full request/response schemas with examples
- Authentication flows (anonymous session_token vs Better Auth cookies)
- Rate limiting rules (10/30/100 req/min by tier)
- Error taxonomy (400/401/404/429/500/503)

Generated quickstart.md with 8-phase implementation:
1. Backend Foundation (health check + DB connections)
2. Content Ingestion Pipeline (MDX parsing + embeddings)
3. Core RAG Endpoint (vector search + LLM streaming)
4. Chat History & Cleanup (pagination + 90-day retention)
5. Authentication Integration (Better Auth middleware + migration)
6. Frontend Chat Widget (React + SSE + localStorage)
7. Observability (structured logging + metrics)
8. Bonus Features (Urdu, personalization, feedback UI)

**Phase 2: Plan Synthesis (Completed)**
Updated plan.md template with:
- Technical context: Python 3.11+, TypeScript 5.x, full tech stack
- Constitution check: All 12 gates passed with justifications
- Project structure: Backend (FastAPI) + Frontend (Docusaurus widget)
- Complexity review: No violations, justified complexity
- Research summary: Key findings from 8 topics
- Data model overview: Postgres + Qdrant schemas
- API contracts: 7 endpoints with authentication flows
- Implementation sequence: 8 phases over 5-7 days
- Deployment strategy: Railway/Render + GitHub Pages
- Risk mitigation: Technical + operational risks with fallbacks
- Success metrics: 28 FRs + 9 SCs with validation checklist

**Agent Context Update (Completed)**
Updated .github/copilot-instructions.md with:
- Added Python 3.11+ (backend), TypeScript 5.x (frontend) to active technologies
- Preserved manual additions between markers

## Outcome

- ✅ Impact: Complete implementation plan generated for RAG chatbot feature (28 FRs, 9 SCs, 8-phase rollout)
- 🧪 Tests: No code tests (planning phase). Testing strategy defined in quickstart.md for each implementation phase.
- 📁 Files: 7 files created/updated (research.md 24KB, data-model.md 15KB, quickstart.md 22KB, contracts 18KB, plan.md 19KB, copilot-instructions.md updated)
- 🔁 Next prompts: Run `/sp.tasks` to break down plan into granular testable tasks, then begin Phase 1 implementation
- 🧠 Reflection: Context7-first approach validated - fetching latest docs prevented outdated patterns (e.g., Better Auth Python SDK doesn't exist, REST API is correct approach). Concurrent API calls efficient for research phase (8 library lookups in parallel). In-memory metrics collector simpler than Prometheus for hackathon scope.

## Evaluation notes (flywheel)

- Failure modes observed: None. Token budget management successful (started at 1M, used ~65K for heavy documentation fetching). Better Auth Python SDK assumption corrected via Context7 lookup (no SDK exists, REST API is official approach).
- Graders run and results (PASS/FAIL): 
  * Constitution gates: PASS (all 12 gates validated with justifications)
  * Spec alignment: PASS (28 FRs mapped to implementation phases, 9 SCs have validation checkpoints)
  * Deliverable completeness: PASS (research.md, data-model.md, quickstart.md, contracts/, plan.md all generated)
  * Technical feasibility: PASS (free tier infrastructure sufficient: Neon 18x headroom, Qdrant 177x headroom, OpenAI < $10/month)
- Prompt variant (if applicable): Standard /sp.plan workflow (Phase 0 → Phase 1 → Phase 2 → Report)
- Next experiment (smallest change to try): Consider streaming ingestion endpoint for large textbook updates (current ingestion is blocking). Could implement with background task queue (Celery) if needed in production. For hackathon, blocking ingestion sufficient.

---

## Command Execution Summary

**Workflow**: /sp.plan (3-phase planning process)

**Phase 0 - Research (completed)**:
- Executed setup-plan.sh → acquired feature paths JSON
- Loaded context: constitution.md (143 lines), spec.md (250 lines), plan template (105 lines)
- Resolved library IDs: FastAPI, Qdrant, OpenAI, Better Auth (4 successful lookups)
- Fetched documentation: 9K tokens of code samples from Context7
- Searched Microsoft Docs: 33 code samples for Postgres + logging
- Created research.md: 24KB comprehensive document with 8 topics

**Phase 1 - Design & Contracts (completed)**:
- Created data-model.md: Postgres schemas (4 tables) + Qdrant collections (2) + relationships + indexes
- Created contracts/openapi-spec.yaml: OpenAPI 3.1 with 7 endpoints, full schemas, authentication flows
- Created contracts/README.md: Validation rules, rate limiting, error taxonomy, testing checklist
- Created quickstart.md: 8-phase implementation guide (5-7 days), acceptance criteria per phase

**Phase 2 - Plan Synthesis (completed)**:
- Updated plan.md: Technical context, constitution check (12 gates), project structure, complexity review
- Updated plan.md: Research summary, data model overview, API contracts, implementation sequence
- Updated plan.md: Deployment strategy, risk mitigation, success metrics (28 FRs + 9 SCs)
- Updated .github/copilot-instructions.md: Added Python 3.11+, TypeScript 5.x to active technologies

**Agent Context Update (completed)**:
- Ran update-agent-context.sh copilot → added language to copilot-instructions.md

**PHR Creation (this file)**:
- Stage: plan
- Route: history/prompts/003-rag-chatbot/
- ID: 0002 (sequential after spec prompt)

**Total Deliverables**: 7 files (6 created, 1 updated)
- specs/003-rag-chatbot/research.md (24KB, 8 topics, 20+ code samples)
- specs/003-rag-chatbot/data-model.md (15KB, 4 tables + 2 collections)
- specs/003-rag-chatbot/quickstart.md (22KB, 8 phases, acceptance criteria)
- specs/003-rag-chatbot/contracts/openapi-spec.yaml (18KB, 7 endpoints)
- specs/003-rag-chatbot/contracts/README.md (8KB, validation + testing)
- specs/003-rag-chatbot/plan.md (19KB, comprehensive plan)
- .github/copilot-instructions.md (updated with tech stack)

**Blockers Removed**: None
**Dependencies Resolved**: All "NEEDS CLARIFICATION" items from spec resolved via Context7
**Ready for Next Phase**: Yes - `/sp.tasks` can now generate granular task breakdown
