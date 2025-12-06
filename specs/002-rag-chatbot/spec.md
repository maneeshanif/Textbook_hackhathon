# Spec: RAG Chatbot for Physical AI Textbook

## Context

Build a Retrieval-Augmented Generation (RAG) chatbot that is embedded within the Docusaurus textbook and can answer questions about Physical AI & Humanoid Robotics content. The chatbot must support both full-book queries and selected-text queries.

## Goals

1. **Ingest textbook content** into a vector database for semantic search
2. **Build FastAPI backend** to handle embedding generation and RAG queries
3. **Embed chat widget** in the Docusaurus frontend
4. **Deploy backend** to cloud (Railway/Cloud Run) with proper authentication

## Requirements

### Core Functionality (Base 100 points)

1. **Vector Database Setup**
   - Use Qdrant Cloud free tier
   - Store embeddings of textbook content (chapters, sections)
   - Support semantic search with OpenAI embeddings

2. **Backend API (FastAPI)**
   - `/ingest` endpoint: Process MDX files → chunks → embeddings → Qdrant
   - `/query` endpoint: Accept user question → retrieve context → generate answer
   - `/query-selection` endpoint: Answer based on user-selected text only
   - Use OpenAI Agents SDK or ChatKit for response generation

3. **Database (Neon Serverless Postgres)**
   - Store chat history
   - Store user sessions
   - Store feedback ratings (optional)

4. **Frontend Chat Widget (React/TypeScript)**
   - Embed in Docusaurus theme
   - Toggle open/close
   - Display streaming responses
   - Support text selection → query mode
   - Show source citations (chapter references)

### Bonus Features

- **Better Auth Integration** (+50): Tie chat history to logged-in users
- **Personalization** (+50): Remember user's preferred chapters, adjust responses
- **Urdu Support** (+50): RAG queries in Urdu, retrieve Urdu-translated content

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Docusaurus Frontend (GitHub Pages/Vercel)         │
│  ┌───────────────────────────────────────────────┐ │
│  │ Book Content (MDX) + Chat Widget (React)     │ │
│  │  ↓                                            │ │
│  │  User Query / Selected Text                  │ │
│  └───────────────┬───────────────────────────────┘ │
│                  │ HTTPS                            │
└──────────────────┼──────────────────────────────────┘
                   ↓
         ┌─────────────────────────┐
         │  FastAPI Backend        │
         │  (Railway/Cloud Run)    │
         │  ┌───────────────────┐  │
         │  │ /ingest           │  │
         │  │ /query            │  │
         │  │ /query-selection  │  │
         │  └─────────┬─────────┘  │
         └────────────┼─────────────┘
                      │
         ┌────────────┼────────────┐
         ↓            ↓             ↓
   ┌─────────┐  ┌─────────┐  ┌──────────┐
   │ OpenAI  │  │ Qdrant  │  │ Neon PG  │
   │ Embed   │  │ Vector  │  │ Chat Log │
   │ + LLM   │  │   DB    │  │  Store   │
   └─────────┘  └─────────┘  └──────────┘
```

## Tech Stack

- **Frontend**: React (Docusaurus custom component), TypeScript
- **Backend**: FastAPI, Python 3.11+
- **Vector DB**: Qdrant Cloud (free tier)
- **Database**: Neon Serverless Postgres
- **AI SDKs**: OpenAI Agents SDK / ChatKit
- **Deployment**: Railway (backend), GitHub Pages (frontend)

## Acceptance Criteria

1. [ ] User can open chat widget on any textbook page
2. [ ] User can ask questions about the book → get accurate answers with citations
3. [ ] User can select text → click "Ask about this" → get contextual answer
4. [ ] Chat history persists in Neon Postgres
5. [ ] Backend is deployed and accessible via HTTPS
6. [ ] Ingestion script processes all MDX files and populates Qdrant
7. [ ] API responses stream back to the frontend
8. [ ] Error handling for API failures, rate limits, etc.

## Non-Goals

- Voice input/output (future enhancement)
- Multi-language chat interface (Urdu is bonus, not required)
- Real-time collaboration features
- Advanced analytics dashboard

## Success Metrics

- **Accuracy**: Chatbot answers correctly using book content
- **Performance**: API response < 3s for typical queries
- **UX**: Chat widget is intuitive, fast, and non-intrusive
- **Reliability**: Backend uptime > 99% during demo period

## Related Artifacts

- `specs/001-docusaurus-book/` — Textbook specification
- `book/` — Docusaurus source code
- `api/` — FastAPI backend (to be created)
- `.env.example` — Environment variables template

## Open Questions

1. How should we handle code blocks in embeddings? (Include or exclude?)
2. What chunk size for MDX content? (e.g., per heading, per paragraph)
3. Should we use function calling for structured queries?
4. Rate limiting strategy for free-tier Qdrant and OpenAI?

## Timeline Estimate

- **Day 1-2**: FastAPI backend setup, Qdrant integration, OpenAI embeddings
- **Day 3-4**: Ingestion script, `/query` and `/query-selection` endpoints
- **Day 5-6**: React chat widget, Docusaurus integration
- **Day 7**: Neon Postgres chat history, Better Auth (bonus)
- **Day 8**: Deployment, testing, polish

---

**Status**: Draft  
**Owner**: maneeshanif  
**Created**: 2025-12-06  
**Last Updated**: 2025-12-06
