# RAG Chatbot — Prompt for Specification

**Goal**: Generate a detailed specification for building a Retrieval-Augmented Generation (RAG) chatbot embedded in the Physical AI textbook.

## Context

We have built a Docusaurus-based textbook for teaching Physical AI & Humanoid Robotics. The book is deployed on GitHub Pages with English and Urdu translations. Now we need to add an intelligent chatbot that:

1. Answers questions about the book content using RAG
2. Handles user-selected text queries (contextual Q&A)
3. Stores chat history in a database
4. Supports authenticated users (Better Auth integration as bonus)

## Requirements from Hackathon

**Core (100 points)**:
- Retrieval-Augmented Generation chatbot
- OpenAI Agents SDK / ChatKit
- FastAPI backend
- Neon Serverless Postgres (chat history)
- Qdrant Cloud free tier (vector embeddings)
- Embedded in Docusaurus book
- Answer questions about book AND selected text

**Bonus**:
- Better Auth integration (+50)
- Personalized responses (+50)
- Urdu translation support (+50)

## Tech Stack

- **Frontend**: React/TypeScript (Docusaurus custom component)
- **Backend**: FastAPI (Python 3.11+)
- **Vector DB**: Qdrant Cloud
- **Database**: Neon Serverless Postgres
- **AI**: OpenAI Embeddings + LLM (via Agents SDK or ChatKit)
- **Deployment**: Railway/Cloud Run (backend), GitHub Pages (frontend)

## What I Need

1. **Detailed Specification Document** covering:
   - Architecture diagram (frontend ↔ backend ↔ databases)
   - API endpoints (`/ingest`, `/query`, `/query-selection`)
   - Data models (chat message, session, user)
   - Ingestion pipeline (MDX → chunks → embeddings → Qdrant)
   - Frontend chat widget design (open/close, streaming, citations)
   - Deployment strategy (Docker, Railway config, env vars)

2. **Implementation Plan** including:
   - Task breakdown (backend, frontend, ingestion, deployment)
   - Acceptance criteria for each task
   - Testing strategy (unit, integration, e2e)

3. **Open Questions** to clarify:
   - Chunk size for MDX content
   - Handling code blocks in embeddings
   - Rate limiting strategy
   - Session management approach

## Output Format

Generate a markdown specification file following this structure:

```markdown
# Spec: RAG Chatbot for Physical AI Textbook

## Context
[High-level problem statement]

## Goals
[What success looks like]

## Requirements
### Core Functionality
[Detailed requirements for base features]

### Bonus Features
[Optional enhancements for extra points]

## Architecture
[Diagram + explanation of components]

## Tech Stack
[List of technologies with justification]

## Acceptance Criteria
[Checklist of deliverables]

## Non-Goals
[What we're NOT building]

## Success Metrics
[How we measure success]

## Open Questions
[Unresolved decisions]

## Timeline Estimate
[Rough breakdown by days/phases]
```

## Instructions for Agent

1. Read the hackathon requirements carefully
2. Consider the existing Docusaurus book structure
3. Design a scalable, maintainable RAG system
4. Prioritize core features over bonuses
5. Provide clear acceptance criteria
6. Identify edge cases and error handling needs
7. Suggest best practices for FastAPI + Qdrant + OpenAI

---

**Expected Output**: `specs/002-rag-chatbot/spec.md`
