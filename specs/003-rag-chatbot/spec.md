# Feature Specification: RAG Chatbot for Physical AI Textbook

**Feature Branch**: `003-rag-chatbot`  
**Created**: 2025-12-06  
**Status**: Active Development  
**Dependencies**: 004-better-auth-implementation (for user authentication)
**Input**: User description: "Build a Retrieval-Augmented Generation (RAG) chatbot embedded in the Physical AI textbook that answers questions about book content, handles user-selected text queries, stores chat history in database, and supports authenticated users"

## ⚠️ Authentication Integration Notice

This feature now integrates with the Better Auth system (Feature 004). Key changes:
- Guest users: 10 free chatbot interactions before requiring authentication
- Authenticated users: Unlimited interactions with persistent history
- See `/specs/004-better-auth/spec.md` for complete auth architecture

## User Scenarios & Testing

### User Story 1 - Basic Question Answering (Priority: P1)

A student reading the textbook encounters an unfamiliar concept and wants clarification without leaving the page or searching elsewhere.

**Why this priority**: Core value proposition - enables instant learning assistance while studying. This is the MVP that makes the chatbot useful.

**Independent Test**: Can be fully tested by opening any textbook page, clicking the chat widget, asking "What is forward kinematics?", and receiving an accurate answer with citations to relevant chapters.

**Acceptance Scenarios**:

1. **Given** user is on any textbook page, **When** user opens chat widget and types a question about book content, **Then** system retrieves relevant context from vector database and generates accurate answer with chapter citations
2. **Given** user asks a question, **When** response is being generated, **Then** answer streams back word-by-word (not all at once) for better UX
3. **Given** user receives an answer with citations, **When** user clicks a citation link, **Then** browser navigates to the referenced chapter/section

---

### User Story 2 - Contextual Selection Queries (Priority: P2)

A student highlights a complex paragraph or code snippet and wants the chatbot to explain that specific content in simpler terms.

**Why this priority**: Enhances learning by providing targeted explanations for difficult passages. Differentiates from generic Q&A.

**Independent Test**: Can be tested by selecting any text on a page, right-clicking or using a "Ask about this" button, and receiving an explanation focused only on the selected content.

**Acceptance Scenarios**:

1. **Given** user selects text on a textbook page, **When** user triggers "Ask about this selection", **Then** chat widget opens with selected text as context and generates explanation based solely on that passage
2. **Given** user has selected text, **When** user asks follow-up questions in the same session, **Then** system maintains the selection context for the conversation
3. **Given** user clears the selection, **When** user asks a new question, **Then** system switches back to full-book query mode

---

### User Story 3 - Persistent Chat History (Priority: P3)

A returning student wants to review their previous questions and answers to reinforce learning.

**Why this priority**: Supports spaced repetition and long-term learning. Valuable but not essential for initial launch.

**Independent Test**: Can be tested by asking several questions across different sessions, logging out and back in, and verifying all chat history is preserved and accessible.

**Acceptance Scenarios**:

1. **Given** user has asked questions in previous sessions, **When** user reopens chat widget, **Then** chat history loads showing previous conversations ordered by recency
2. **Given** user is logged in (bonus feature), **When** user accesses chatbot from different device, **Then** chat history syncs across devices
3. **Given** user wants to clear history, **When** user clicks "Clear history" button, **Then** system archives history in database but removes from view

---

### User Story 4 - Multi-Language Support (Priority: P4 - Bonus)

An Urdu-speaking student wants to ask questions in Urdu and receive answers based on Urdu-translated textbook content.

**Why this priority**: Bonus feature (+50 points) that significantly expands accessibility but not required for core functionality.

**Independent Test**: Can be tested by switching language toggle to Urdu, asking a question in Urdu script, and receiving an answer that cites Urdu content from `i18n/ur/` directory.

**Acceptance Scenarios**:

1. **Given** user selects Urdu language, **When** user asks question in Urdu, **Then** system searches Urdu content embeddings and responds in Urdu
2. **Given** user switches between English and Urdu mid-conversation, **When** user asks a question, **Then** system responds in the currently selected language

---

### Edge Cases

- What happens when user asks a question completely unrelated to the textbook (e.g., "What's the weather today")?
  - System should politely decline and suggest refocusing on Physical AI topics
- How does system handle when Qdrant vector database is temporarily unavailable?
  - Display user-friendly error message: "Search service temporarily unavailable. Please try again shortly."
- What if user selects an extremely long passage (5000+ words)?
  - Truncate selection to first 2000 tokens and warn user that only partial selection was used
- How does system handle malformed or adversarial inputs (prompt injection attempts)?
  - Sanitize inputs, use system prompts to keep responses focused on educational content only
- What if user is not authenticated but tries to access chat history?
  - Store chat history in browser localStorage for anonymous users (session-only), prompt to sign up for cross-device sync
- How does system handle session handoff when anonymous user authenticates?
  - Migrate localStorage chat history to database upon login, preserve conversation continuity
- What if vector search returns no results with sufficient similarity score?
  - Display fallback message: "I couldn't find relevant information in the textbook for this question. Try rephrasing or check the table of contents." 
  - Log query for content gap analysis

## Requirements

### Functional Requirements

- **FR-001**: System MUST embed a chat widget on every textbook page that can be toggled open/closed
- **FR-002**: System MUST accept natural language questions from users via text input
- **FR-003**: System MUST retrieve semantically relevant textbook content from vector database based on user query
- **FR-004**: System MUST enforce minimum similarity threshold (0.7 cosine similarity) for retrieved chunks and display fallback message when no results meet threshold
- **FR-005**: System MUST generate answers using large language model with retrieved content as context
- **FR-006**: System MUST cite specific chapters/sections in the answer (e.g., "See Section 2.1.3 — Robot Dynamics")
- **FR-007**: System MUST support "Ask about this selection" mode where user highlights text and queries about only that passage
- **FR-008**: System MUST stream API responses token-by-token to provide responsive UI experience
- **FR-009**: System MUST store all chat messages (user queries and bot responses) in persistent database
- **FR-010**: System MUST allow guest (unauthenticated) users to use chatbot with localStorage-based session storage
- **FR-011**: System MUST prompt guest users to authenticate after 5 messages with benefits messaging (unlimited history, cross-device sync, personalization)
- **FR-012**: System MUST migrate localStorage chat history to database when guest user authenticates
- **FR-013**: System MUST handle API errors gracefully with user-friendly messages (no stack traces shown to users)
- **FR-014**: System MUST limit anonymous users to 20 messages per day to prevent abuse (tracked via browser fingerprint or IP)
- **FR-015**: System MUST process and embed all MDX textbook files during ingestion phase
- **FR-016**: System MUST chunk textbook content into semantically meaningful segments (approximately 500 tokens per chunk with 50-token overlap)
- **FR-017**: System MUST exclude code blocks from embeddings to reduce noise (assumption: code explanations in prose are more valuable than raw code for semantic search)
- **FR-018**: System MUST provide API endpoint for administrative content re-ingestion when textbook is updated
- **FR-019**: Users MUST be able to rate answers (thumbs up/down) to collect feedback data
- **FR-020**: System MUST retain chat history for 90 days for anonymous sessions and unlimited retention for authenticated users
- **FR-021**: System MUST log queries that fall below similarity threshold to identify content gaps and improve retrieval quality
- **FR-022** (Bonus): System MUST integrate Better Auth for user authentication with email/password and OAuth providers
- **FR-023** (Bonus): System MUST support Urdu language queries and retrieve from Urdu-translated content when user selects Urdu language
- **FR-024** (Bonus): Authenticated users MUST have chat history synced across devices and sessions
- **FR-025** (Bonus): System MUST personalize responses based on user's reading history and preferred chapters
- **FR-026**: System MUST emit structured JSON logs to stdout with request ID, user context, query text, retrieval results, and response times
- **FR-027**: System MUST track operational metrics including query volume, error rates, latency percentiles (p50, p95, p99), and vector search quality scores
- **FR-028**: System MUST include request tracing IDs in API responses and logs to enable end-to-end debugging of failed queries

### Key Entities

- **Chat Message**: Represents a single message in a conversation (user question or bot answer), with timestamp, content, and citations
- **Chat Session**: Groups related messages into a conversation thread, associated with a user (or anonymous session ID)
- **Vector Chunk**: A segment of textbook content stored in vector database with embedding, metadata (chapter, section, language)
- **User** (Bonus): Authenticated user account with preferences and cross-device chat history

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can receive relevant answers to textbook questions within 3 seconds of submitting query
- **SC-002**: System accurately answers 90% of questions verifiable against textbook content (measured by human evaluation sample)
- **SC-003**: Chat widget loads on page within 500ms and does not slow down textbook page rendering
- **SC-004**: Backend API handles at least 50 concurrent users without degradation in response time
- **SC-005**: All API errors are traceable via request IDs with full context (query, user, error type) logged for debugging
- **SC-005**: All API errors are traceable via request IDs with full context (query, user, error type) logged for debugging
- **SC-006**: 80% of users who try the chatbot ask at least 2 follow-up questions in same session (indicates engagement)
- **SC-007**: System maintains 99% uptime during evaluation period (demo week)
- **SC-008**: Positive user feedback rate (thumbs up vs down) exceeds 75%
- **SC-009**: Selected text queries return answers focused on selection content in 100% of test cases

---

## Clarifications

### Chat History Retention (2025-12-06)
**Decision**: Implement 90-day retention for anonymous sessions and unlimited retention for authenticated users.

**Rationale**: 
- Balances storage costs for anonymous usage
- Incentivizes user authentication for premium experience (aligns with Better Auth bonus feature)
- 90 days provides sufficient time for course completion while limiting database growth
- Unlimited retention for authenticated users supports long-term learning and review patterns

**Impact**: 
- Database schema must include `created_at` timestamp on chat sessions
- Background cleanup job required to purge anonymous sessions older than 90 days
- Authentication integration becomes more valuable to users (stronger conversion incentive)

### Authentication Strategy (2025-12-06)
**Decision**: Implement guest access with upgrade prompts to authenticated accounts.

**Rationale**:
- Low-friction onboarding: Students can try chatbot immediately without signup barrier
- Progressive engagement: Prompt to authenticate after 5 messages when value is demonstrated
- Clear upgrade incentive: Authentication unlocks unlimited history, cross-device sync, and personalization
- Maximizes bonus points: Demonstrates Better Auth integration (+50 points) while maintaining usability

**Implementation Requirements**:
- Guest sessions stored in browser localStorage (temporary, single-device)
- Upgrade prompt appears after 5th message with benefits list
- Session migration: localStorage history transferred to database on login
- Better Auth integration with email/password + OAuth providers (Google, GitHub)
- Rate limiting: 20 messages/day for anonymous users, unlimited for authenticated

**Impact**:
- Frontend must handle dual storage strategy (localStorage vs API)
- Backend API requires auth middleware with guest/authenticated routing
- UX must communicate value proposition clearly at upgrade prompt
- Session handoff logic required to preserve conversation continuity

### Observability Strategy (2025-12-06)
**Decision**: Implement structured logging with basic operational metrics (no enterprise APM tools).

**Rationale**:
- Structured JSON logs enable queryable debugging without expensive third-party tools
- FastAPI middleware + Python `logging` module = minimal setup overhead
- Docker-friendly stdout logging supports standard container orchestration practices
- Request tracing IDs allow end-to-end debugging of user issues without session replay tools
- Basic metrics (latency, error rates, query volume) sufficient for hackathon demonstration and production monitoring

**Logging Requirements**:
- Format: JSON with fields: `timestamp`, `request_id`, `user_id/session_id`, `query_text`, `retrieval_chunks`, `response_time_ms`, `error_type`, `http_status`
- Output: stdout (captured by Docker/systemd logs)
- Log Levels: ERROR (failures), WARN (degraded performance), INFO (successful queries with metrics)

**Metrics to Track**:
- Query volume (total, per-user, per-hour)
- Error rates by type (vector_search_failed, llm_timeout, database_error)
- Latency percentiles (p50, p95, p99) for full request and each component (retrieval, LLM, database)
- Vector search quality: average similarity scores, chunk relevance ratings

**Tools**:
- Python `logging` with `structlog` for JSON formatting
- FastAPI middleware for request tracing
- Optional: Prometheus-compatible metrics endpoint for grafana visualization (bonus, not required)

**Impact**:
- All API routes must use centralized logging middleware
- Request IDs generated at entry point and passed through all service layers
- Error handling must capture and log full context before returning user-friendly messages
- Performance overhead: ~5-10ms per request (acceptable for 3s latency target)

### Vector Search Quality Control (2025-12-06)
**Decision**: Enforce minimum similarity threshold (0.7 cosine similarity) with transparent fallback messaging.

**Rationale**:
- Prevents hallucination from irrelevant retrieved chunks (common RAG failure mode)
- Transparent communication builds user trust ("I don't know" better than confident wrong answers)
- Threshold is configurable via environment variable for post-launch tuning
- Queries below threshold provide valuable signal for content gap analysis and embedding quality improvement

**Fallback Behavior**:
- **Threshold**: 0.7 cosine similarity (adjustable)
- **User Message**: "I couldn't find relevant information in the textbook for this question. Try rephrasing or check the table of contents."
- **Logging**: Capture full query text, top-k similarity scores, and user context for analysis
- **Metric**: Track percentage of queries below threshold (target: <10% rejection rate)

**Quality Validation**:
- Manual review of rejected queries during testing phase
- A/B test threshold values (0.65, 0.70, 0.75) to optimize precision/recall trade-off
- User feedback on "not found" responses helps calibrate threshold

**Impact**:
- Retrieval pipeline must compute and return similarity scores with each result
- API response includes `retrieval_quality` field with score and threshold status
- Content ingestion quality becomes critical (chunking strategy, embedding model choice)
- May require fallback to keyword search for edge cases (future enhancement)

---

**Status**: Draft  
**Owner**: maneeshanif  
**Created**: 2025-12-06  
**Last Updated**: 2025-12-06
