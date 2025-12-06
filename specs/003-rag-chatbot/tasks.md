# Tasks: RAG Chatbot for Physical AI Textbook

**Feature**: 003-rag-chatbot  
**Branch**: `003-rag-chatbot`  
**Date**: 2025-12-06  
**Input**: Design documents from `/specs/003-rag-chatbot/`

## Overview

This task list organizes implementation work by user story to enable independent development and testing. Each phase delivers a testable increment that can be validated independently.

**Tests**: Not explicitly requested in specification - focusing on core functionality implementation with manual testing.

**Organization Strategy**:
- Phase 1: Setup (project initialization, infrastructure)
- Phase 2: Foundational (blocking prerequisites for all stories)
- Phase 3-6: User Stories (P1-P4 in priority order)
- Phase 7: Polish & Cross-Cutting Concerns

**Total Tasks**: 68 tasks across 7 phases  
**Estimated Timeline**: 5-7 days for hackathon implementation

---

## Format Convention

**Task Format**: `- [ ] [ID] [P?] [Story?] Description with file path`

- **Checkbox**: `- [ ]` for incomplete, `- [x]` for complete
- **[ID]**: Sequential task number (T001, T002, etc.)
- **[P]**: Parallelizable (different files, no blocking dependencies)
- **[Story]**: User story label (US1, US2, US3, US4) - only for story-specific tasks
- **Description**: Clear action with exact file path

**Examples**:
- `- [ ] T001 Create project structure per implementation plan`
- `- [ ] T015 [P] [US1] Implement RAG service in rag-chatbot-backend/app/services/rag.py`
- `- [ ] T025 [US2] Add selection context handling in rag-chatbot-backend/app/api/chat.py`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure, configure infrastructure, establish foundational patterns

**Duration**: Day 1, 2-3 hours

### Backend Setup

- [x] T001 Create backend directory structure: `rag-chatbot-backend/` with subdirs: `app/`, `scripts/`, `tests/`, `migrations/`
- [x] T002 Initialize Python virtual environment and install dependencies: `fastapi==0.109+`, `uvicorn`, `asyncpg==0.29+`, `qdrant-client==1.7+`, `google-genai==1.33+`, `structlog==24.1+`, `pydantic-settings`, `python-dotenv`
- [x] T003 [P] Create `.env.example` with all 12 required environment variables (NEON_CONNECTION_STRING, QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY, etc.)
- [x] T004 [P] Create `requirements.txt` with pinned dependency versions from plan.md
- [x] T005 [P] Setup Dockerfile for Railway/Render deployment in `rag-chatbot-backend/Dockerfile`

### Frontend Setup

- [x] T006 Create React widget directory structure: `book/src/components/ChatWidget/` with subdirs: `components/`, `hooks/`, `utils/`, `types/`
- [x] T007 Install frontend dependencies: `react-markdown`, `eventsource` polyfill, testing libraries
- [x] T008 [P] Create TypeScript types for chat messages, sessions, API responses in `book/src/components/ChatWidget/types/index.ts`

### Infrastructure Setup

- [ ] T009 Create Neon Postgres database and obtain connection string
- [ ] T010 Create Qdrant Cloud collection for English content: `textbook_chunks_en` (768 dimensions, cosine similarity)
- [ ] T011 [P] Create Qdrant Cloud collection for Urdu content: `textbook_chunks_ur` (768 dimensions, cosine similarity)
- [ ] T012 [P] Obtain Gemini API key from Google AI Studio
- [ ] T013 [P] Setup Railway/Render account and create new project

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before user stories can be implemented

**Duration**: Day 1-2, 3-4 hours

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Foundation

- [ ] T014 Create SQL migration for `users` table in `rag-chatbot-backend/migrations/001_create_users.sql`
- [ ] T015 Create SQL migration for `chat_sessions` table with indexes in `rag-chatbot-backend/migrations/002_create_sessions.sql`
- [ ] T016 Create SQL migration for `chat_messages` table with indexes in `rag-chatbot-backend/migrations/003_create_messages.sql`
- [ ] T017 Create SQL migration for `feedback` table in `rag-chatbot-backend/migrations/004_create_feedback.sql`
- [ ] T018 Run all migrations against Neon database and verify schema

### Core Backend Services

- [ ] T019 Implement configuration loading with Pydantic in `rag-chatbot-backend/app/config.py`
- [ ] T020 Create asyncpg connection pool manager in `rag-chatbot-backend/app/database.py`
- [ ] T021 Create Qdrant async client wrapper in `rag-chatbot-backend/app/qdrant_client.py`
- [ ] T022 [P] Initialize Gemini client in `rag-chatbot-backend/app/gemini_client.py`
- [ ] T023 Implement FastAPI app with CORS middleware in `rag-chatbot-backend/app/main.py`
- [ ] T024 Create health check endpoint in `rag-chatbot-backend/app/api/health.py` (checks Postgres, Qdrant, Gemini)

### Request Infrastructure

- [ ] T025 [P] Implement request tracing middleware with UUID generation in `rag-chatbot-backend/app/middleware/logging.py`
- [ ] T026 [P] Setup structured JSON logging with structlog in `rag-chatbot-backend/app/middleware/logging.py`
- [ ] T027 [P] Create Pydantic schemas for all API requests/responses in `rag-chatbot-backend/app/models/schemas.py`

### Content Ingestion (Must complete before US1)

- [ ] T028 Create MDX parser script (exclude code blocks, 500-token chunks, 50-token overlap) in `rag-chatbot-backend/scripts/parse_mdx.py`
- [ ] T029 Implement batch embedding function using Gemini text-embedding-004 in `rag-chatbot-backend/app/services/ingestion.py`
- [ ] T030 Create Qdrant upsert script for chunks in `rag-chatbot-backend/scripts/ingest_textbook.py`
- [ ] T031 Run ingestion pipeline for English content (`book/docs/**/*.mdx` → `textbook_chunks_en`)
- [ ] T032 Verify vector search quality: Query "what is forward kinematics" returns relevant chunks with > 0.7 similarity

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Question Answering (Priority: P1) 🎯 MVP

**Goal**: Students can ask questions about textbook content and receive AI-generated answers with chapter citations

**Independent Test**: Open any textbook page, click chat widget, ask "What is forward kinematics?", receive accurate answer with citations to relevant chapters within 3 seconds

**Why This is MVP**: Core value proposition - instant learning assistance while studying

**Duration**: Day 2-3, 4-5 hours

### Backend Implementation

- [ ] T033 [US1] Implement vector search function in `rag-chatbot-backend/app/services/rag.py` (query embedding → Qdrant search with 0.7 threshold)
- [ ] T034 [US1] Implement LLM streaming function with Gemini gemini-2.0-flash-exp in `rag-chatbot-backend/app/services/rag.py`
- [ ] T035 [US1] Create RAG pipeline: search → format context → stream response in `rag-chatbot-backend/app/services/rag.py`
- [ ] T036 [US1] Implement `/api/chat/query` endpoint (POST) with SSE streaming in `rag-chatbot-backend/app/api/chat.py`
- [ ] T037 [US1] Add citation extraction logic (return chapter IDs from retrieved chunks) in `rag-chatbot-backend/app/services/rag.py`
- [ ] T038 [US1] Handle fallback message when no results above 0.7 similarity threshold in `rag-chatbot-backend/app/api/chat.py`

### Frontend Implementation

- [ ] T039 [P] [US1] Create ChatWidget component with open/close toggle in `book/src/components/ChatWidget/ChatWidget.tsx`
- [ ] T040 [P] [US1] Create MessageList component displaying user/assistant messages in `book/src/components/ChatWidget/components/MessageList.tsx`
- [ ] T041 [P] [US1] Create InputBox component with send button in `book/src/components/ChatWidget/components/InputBox.tsx`
- [ ] T042 [US1] Implement SSE client hook for streaming responses in `book/src/components/ChatWidget/hooks/useStreamingQuery.ts`
- [ ] T043 [US1] Add citation links that navigate to chapter sections in `book/src/components/ChatWidget/components/Message.tsx`
- [ ] T044 [US1] Style chat widget (floating button, panel UI, responsive) in `book/src/components/ChatWidget/ChatWidget.module.css`
- [ ] T045 [US1] Embed ChatWidget in Docusaurus theme wrapper at `book/src/theme/Root.tsx`

### Integration & Validation

- [ ] T046 [US1] Test query: "What is forward kinematics?" returns answer with citations
- [ ] T047 [US1] Test streaming: Verify response appears word-by-word (not all at once)
- [ ] T048 [US1] Test citation clicks: Links navigate to correct chapter sections
- [ ] T049 [US1] Test fallback: Query "What's the weather?" triggers "not found" message
- [ ] T050 [US1] Measure latency: Confirm < 3s total response time and < 500ms first chunk

---

## Phase 4: User Story 2 - Contextual Selection Queries (Priority: P2)

**Goal**: Students can highlight text and ask chatbot to explain that specific content

**Independent Test**: Select any paragraph on a page, click "Ask about this selection", receive explanation focused only on selected content

**Why P2**: Enhances learning with targeted explanations - differentiates from generic Q&A

**Duration**: Day 3, 2-3 hours

### Backend Implementation

- [ ] T051 [US2] Implement `/api/chat/query-selection` endpoint (POST) accepting `query` + `selected_text` in `rag-chatbot-backend/app/api/chat.py`
- [ ] T052 [US2] Modify RAG service to use selected text as additional context in system prompt in `rag-chatbot-backend/app/services/rag.py`
- [ ] T053 [US2] Add selection context persistence in session (track last selection for follow-ups) in `rag-chatbot-backend/app/api/chat.py`

### Frontend Implementation

- [ ] T054 [P] [US2] Add text selection detection listener in `book/src/components/ChatWidget/hooks/useTextSelection.ts`
- [ ] T055 [P] [US2] Create "Ask about this selection" button/tooltip on text selection in `book/src/components/ChatWidget/components/SelectionPrompt.tsx`
- [ ] T056 [US2] Populate InputBox with selected text context when triggered in `book/src/components/ChatWidget/ChatWidget.tsx`
- [ ] T057 [US2] Display selected text indicator in chat UI in `book/src/components/ChatWidget/components/MessageList.tsx`
- [ ] T058 [US2] Add "Clear selection" button to return to full-book mode in `book/src/components/ChatWidget/ChatWidget.tsx`

### Integration & Validation

- [ ] T059 [US2] Test: Select paragraph about "inverse kinematics", click "Ask", verify answer focuses on selection
- [ ] T060 [US2] Test: Ask follow-up question, verify context persists
- [ ] T061 [US2] Test: Clear selection, ask new question, verify switched back to full-book mode

---

## Phase 5: User Story 3 - Persistent Chat History (Priority: P3)

**Goal**: Returning students can review previous questions and answers for spaced repetition

**Independent Test**: Ask several questions, refresh browser, verify chat history loads with previous conversations ordered by recency

**Why P3**: Supports long-term learning but not essential for initial launch

**Duration**: Day 4, 3-4 hours

### Backend Implementation

- [ ] T062 [US3] Implement session creation logic (generate session_token for anonymous users) in `rag-chatbot-backend/app/services/session.py`
- [ ] T063 [US3] Save user queries and assistant responses to `chat_messages` table in `rag-chatbot-backend/app/api/chat.py`
- [ ] T064 [US3] Implement `/api/chat/history` endpoint (GET) returning session messages in `rag-chatbot-backend/app/api/chat.py`
- [ ] T065 [US3] Add pagination for history (limit 50 messages per page) in `rag-chatbot-backend/app/api/chat.py`

### Frontend Implementation

- [ ] T066 [P] [US3] Implement localStorage session token management in `book/src/components/ChatWidget/utils/session.ts`
- [ ] T067 [P] [US3] Create history loading hook on widget mount in `book/src/components/ChatWidget/hooks/useHistory.ts`
- [ ] T068 [US3] Display loading state while fetching history in `book/src/components/ChatWidget/components/MessageList.tsx`
- [ ] T069 [US3] Add "Load more" button for paginated history in `book/src/components/ChatWidget/components/MessageList.tsx`
- [ ] T070 [US3] Persist new messages to localStorage after each query in `book/src/components/ChatWidget/hooks/useStreamingQuery.ts`

### Integration & Validation

- [ ] T071 [US3] Test: Ask 3 questions, refresh page, verify all 3 appear in history
- [ ] T072 [US3] Test: Ask 51 questions, verify pagination with "Load more"
- [ ] T073 [US3] Test: Open chat on different device (same session token in localStorage), verify history syncs

---

## Phase 6: User Story 4 - Multi-Language Support (Priority: P4 - Bonus)

**Goal**: Urdu-speaking students can ask questions in Urdu and receive answers from Urdu textbook content

**Independent Test**: Switch language toggle to Urdu, ask question in Urdu script, receive answer citing Urdu content from `i18n/ur/` directory

**Why P4 Bonus**: +50 points for internationalization, significantly expands accessibility but not required for core functionality

**Duration**: Day 5, 2-3 hours

### Backend Implementation

- [ ] T074 [US4] Run ingestion pipeline for Urdu content (`book/i18n/ur/docusaurus-plugin-content-docs/current/**/*.mdx` → `textbook_chunks_ur`)
- [ ] T075 [US4] Add `language` parameter to `/api/chat/query` endpoint in `rag-chatbot-backend/app/api/chat.py`
- [ ] T076 [US4] Route query to correct Qdrant collection based on language (`textbook_chunks_en` vs `textbook_chunks_ur`) in `rag-chatbot-backend/app/services/rag.py`
- [ ] T077 [US4] Update session creation to track language preference in `rag-chatbot-backend/app/services/session.py`

### Frontend Implementation

- [ ] T078 [P] [US4] Add language toggle button (EN/UR) to chat widget header in `book/src/components/ChatWidget/components/Header.tsx`
- [ ] T079 [P] [US4] Detect current Docusaurus locale and default chat language in `book/src/components/ChatWidget/hooks/useLocale.ts`
- [ ] T080 [US4] Update API calls to include language parameter in `book/src/components/ChatWidget/hooks/useStreamingQuery.ts`
- [ ] T081 [US4] Apply RTL styling when language is Urdu in `book/src/components/ChatWidget/ChatWidget.module.css`

### Integration & Validation

- [ ] T082 [US4] Test: Switch to Urdu, ask "یہ کیا ہے؟" (what is this?), verify response in Urdu
- [ ] T083 [US4] Test: Switch back to English mid-conversation, verify language changes
- [ ] T084 [US4] Test: Open Urdu page (`/ur/docs/...`), verify chat defaults to Urdu language

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Features that span multiple user stories - authentication, feedback, observability, performance

**Duration**: Day 5-6, 4-5 hours

### Authentication & Migration (Bonus)

- [ ] T085 Setup Better Auth configuration with email/password + OAuth providers
- [ ] T086 Implement auth middleware for session validation in `rag-chatbot-backend/app/middleware/auth.py`
- [ ] T087 Create `/api/chat/migrate` endpoint (POST) for localStorage → database migration in `rag-chatbot-backend/app/api/chat.py`
- [ ] T088 [P] Add "Sign up for unlimited history" prompt after 5 messages in `book/src/components/ChatWidget/components/UpgradePrompt.tsx`
- [ ] T089 [P] Implement auth flow in frontend (login button, callback handling) in `book/src/components/ChatWidget/components/AuthButton.tsx`

### Feedback Collection

- [ ] T090 [P] Implement `/api/chat/feedback` endpoint (POST) saving thumbs up/down in `rag-chatbot-backend/app/api/chat.py`
- [ ] T091 [P] Add thumbs up/down buttons to each assistant message in `book/src/components/ChatWidget/components/Message.tsx`
- [ ] T092 [P] Track feedback submission state (prevent duplicate votes) in `book/src/components/ChatWidget/hooks/useFeedback.ts`

### Observability & Monitoring

- [ ] T093 Add request ID to all log entries and error responses in `rag-chatbot-backend/app/middleware/logging.py`
- [ ] T094 [P] Log query text, retrieval chunks, similarity scores for quality analysis in `rag-chatbot-backend/app/services/rag.py`
- [ ] T095 [P] Implement metrics collector (query volume, latency percentiles, error rates) in `rag-chatbot-backend/app/services/metrics.py`
- [ ] T096 [P] Create `/api/admin/metrics` endpoint (GET) for dashboard in `rag-chatbot-backend/app/api/admin.py`

### Rate Limiting & Security

- [ ] T097 Implement rate limiting middleware (10 req/min anonymous, 30 req/min authenticated) in `rag-chatbot-backend/app/middleware/rate_limit.py`
- [ ] T098 [P] Add input sanitization for user queries (max 2000 chars, remove control characters) in `rag-chatbot-backend/app/api/chat.py`
- [ ] T099 [P] Implement admin API key authentication for `/api/admin/*` endpoints in `rag-chatbot-backend/app/middleware/auth.py`

### Performance & Optimization

- [ ] T100 Add database indexes for common queries (session_id, user_id, created_at) - verify from migrations
- [ ] T101 [P] Implement connection pooling for Postgres (min 5, max 20 connections) in `rag-chatbot-backend/app/database.py`
- [ ] T102 [P] Add response caching for identical queries within 1-hour window (simple in-memory LRU cache) in `rag-chatbot-backend/app/services/rag.py`

### Background Jobs

- [ ] T103 Create cleanup job for 90-day retention (delete old anonymous sessions) in `rag-chatbot-backend/scripts/cleanup_old_sessions.py`
- [ ] T104 [P] Create query gap analysis script (log queries below 0.7 threshold) in `rag-chatbot-backend/scripts/analyze_query_gaps.py`

### Deployment

- [ ] T105 Create Railway deployment configuration (`railway.json` or `Procfile`) in `rag-chatbot-backend/`
- [ ] T106 [P] Update Docusaurus build config to include chat widget in static build in `book/docusaurus.config.ts`
- [ ] T107 Deploy backend to Railway and verify health check passes
- [ ] T108 Deploy frontend to GitHub Pages and verify chat widget loads
- [ ] T109 Update frontend API endpoint URLs to production backend in `book/src/components/ChatWidget/config.ts`

---

## Dependencies & Execution Strategy

### Critical Path (Must Complete Sequentially)

```
Phase 1 (Setup) → Phase 2 (Foundation) → Phase 3 (US1 - MVP) → Deploy MVP
```

**Minimum Viable Product (MVP)**: Complete through Phase 3 (User Story 1) for basic Q&A functionality

### Parallel Opportunities

**After Phase 2 completes**, these can be developed independently:
- User Story 2 (Selection Queries) - independent from US1
- User Story 3 (Chat History) - uses same backend API patterns as US1
- User Story 4 (Multi-Language) - parallel Qdrant collection, no conflicts

**Within each user story phase**:
- Backend and frontend tasks with `[P]` marker can run in parallel
- Example: In US1, T039-T045 (all frontend) can be developed while T033-T038 (backend) are in progress

### Incremental Delivery Strategy

1. **Day 1-2**: Complete Phase 1 + Phase 2 → Health check endpoint functional
2. **Day 2-3**: Complete Phase 3 (US1) → Deploy MVP with basic Q&A
3. **Day 3-4**: Add Phase 4 (US2) + Phase 5 (US3) → Enhanced UX with history
4. **Day 5**: Add Phase 6 (US4 Bonus) → Multi-language support (+50 points)
5. **Day 5-6**: Complete Phase 7 → Polish, auth, observability
6. **Day 7**: Load testing, bug fixes, demo preparation

### Independent Story Testing

Each user story can be validated independently:

- **US1 Test**: Open any page → ask question → receive answer with citations (< 3s)
- **US2 Test**: Select text → ask about selection → verify focused explanation
- **US3 Test**: Ask questions → refresh → verify history loads
- **US4 Test**: Switch to Urdu → ask in Urdu → verify Urdu response

---

## Task Summary

**Total Tasks**: 109 tasks across 7 phases

### Breakdown by Phase:
- Phase 1 (Setup): 13 tasks
- Phase 2 (Foundation): 19 tasks (blocking)
- Phase 3 (US1 - MVP): 18 tasks
- Phase 4 (US2): 11 tasks
- Phase 5 (US3): 12 tasks
- Phase 6 (US4 - Bonus): 11 tasks
- Phase 7 (Polish): 25 tasks

### Parallelization Potential:
- **Setup Phase**: 5 parallel tasks (T003, T004, T005, T008, T011-T013)
- **Foundation Phase**: 6 parallel tasks (T022, T025-T027)
- **US1 Phase**: 4 parallel tasks (T039-T041)
- **US2 Phase**: 2 parallel tasks (T054-T055)
- **US3 Phase**: 2 parallel tasks (T066-T067)
- **US4 Phase**: 2 parallel tasks (T078-T079)
- **Polish Phase**: 12 parallel tasks (various)

**Total Parallel Opportunities**: 33 tasks can be executed concurrently with proper team coordination

### MVP Scope (Recommended for Initial Launch)

**Minimum**: Complete through Phase 3 (43 tasks)
- Basic question answering with citations
- Streaming responses
- Chat widget integration
- Health check and error handling

**Target**: Complete through Phase 5 (66 tasks)
- Add selection queries
- Add persistent history
- Better user engagement and retention

**Full Feature Set**: All 109 tasks
- Multi-language support (+50 bonus points)
- Authentication and migration
- Feedback collection
- Full observability

---

## Validation Checklist

**Format Validation**:
- ✅ All tasks follow `- [ ] [ID] [P?] [Story?] Description with file path` format
- ✅ Sequential task IDs (T001 through T109)
- ✅ Story labels present on all user story tasks (US1, US2, US3, US4)
- ✅ File paths included in all implementation tasks
- ✅ Parallelization markers `[P]` on independent tasks

**Organization Validation**:
- ✅ Tasks organized by user story (Phase 3-6)
- ✅ Each story phase includes goal and independent test criteria
- ✅ Foundation phase (Phase 2) marked as blocking
- ✅ Dependencies documented with clear critical path

**Completeness Validation**:
- ✅ All 28 functional requirements from spec.md covered
- ✅ All 4 user stories (P1-P4) mapped to task phases
- ✅ All entities from data-model.md included (users, sessions, messages, feedback)
- ✅ All 7 API endpoints from contracts/ mapped to tasks
- ✅ Deployment and observability included in Phase 7

---

**Generated**: 2025-12-06  
**Status**: Ready for implementation  
**Next Step**: Begin Phase 1 (Setup) tasks T001-T013
