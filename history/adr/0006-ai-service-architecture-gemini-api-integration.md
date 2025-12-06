# ADR-0006: AI Service Architecture - Gemini API Integration

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-06
- **Feature:** 003-rag-chatbot
- **Context:** RAG chatbot requires two AI capabilities: (1) text embeddings for semantic search over textbook content (800 chunks, 768 dimensions), and (2) streaming chat completions for generating answers with citations. Budget constraint is critical for hackathon: target < $5/month for 500 queries/day. Must support multilingual content (English/Urdu) and maintain quality comparable to GPT-4 for technical explanations. Originally planned with OpenAI but pivoted to Gemini for cost savings and generous free tier.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core AI service, affects quality and cost
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - OpenAI, Anthropic, local models
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Impacts embeddings, chat, ingestion, quality
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use Google Gemini API for all AI operations with the following integrated architecture:

- **Embeddings Model**: `text-embedding-004` (768 dimensions, configurable 1-768)
- **Chat Model**: `gemini-2.0-flash-exp` with streaming support
- **SDK**: `google-genai` 1.33+ Python package
- **Cost Model**: FREE tier (1500 requests/day) - sufficient for 500 queries/day target
- **API Key Management**: Single `GEMINI_API_KEY` environment variable
- **Task Type Optimization**: `RETRIEVAL_DOCUMENT` for embeddings (optimized for semantic search)
- **Streaming Pattern**: `generate_content_stream()` for token-by-token responses

## Consequences

### Positive

- **100% Free for Hackathon**: 1500 requests/day free tier vs $0.60/month with OpenAI (cost savings: $0.60/month)
- **Smaller Embeddings**: 768 dimensions vs 1536 (OpenAI) saves 50% storage (3.2 MB vs 5.6 MB in Qdrant)
- **Fast Inference**: gemini-2.0-flash-exp optimized for low latency (< 500ms first chunk target achievable)
- **Simpler Streaming**: `generate_content_stream()` API simpler than OpenAI's async context managers
- **Multimodal Ready**: Future support for diagram/image explanations (currently text-only)
- **Generous Rate Limits**: 1500 req/day sufficient for 50+ concurrent users in hackathon
- **Better Free Tier Utilization**: Qdrant 311x headroom (vs 177x with OpenAI's larger embeddings)

### Negative

- **Newer API**: Less battle-tested than OpenAI (launched 2024 vs OpenAI's mature ecosystem)
- **Vendor Lock-in**: Switching to OpenAI/Anthropic later requires re-embedding all 800 chunks
- **Dimension Change Risk**: If quality insufficient, upgrading to OpenAI means larger storage footprint
- **Limited Documentation**: google-genai Python SDK has fewer community examples than openai package
- **No Structured Outputs**: Gemini doesn't support JSON schema enforcement like OpenAI (citations parsed from text)
- **Free Tier Uncertainty**: Google could reduce free tier limits (mitigation: monitor usage, have OpenAI fallback plan)

## Alternatives Considered

**Alternative A: OpenAI (text-embedding-3-small + gpt-4o)**
- Pros: Mature ecosystem, structured outputs support, extensive documentation, proven quality
- Cons: Cost $0.60/month for 500 queries/day, larger embeddings (1536-dim = more storage), paid tier required
- Rejected: Free tier advantage of Gemini critical for hackathon budget constraints

**Alternative B: Anthropic Claude (Embeddings + Claude 3.5 Sonnet)**
- Pros: Superior reasoning quality, longer context windows (200K tokens)
- Cons: No official embeddings model (requires Voyage AI integration = 2 vendors), expensive ($3/million tokens), overkill for textbook Q&A
- Rejected: Complexity of multi-vendor setup, cost prohibitive for hackathon

**Alternative C: Local Models (sentence-transformers + Ollama)**
- Pros: Zero API costs, full control, no rate limits, offline capability
- Cons: Requires GPU for acceptable performance (hackathon servers CPU-only), lower quality embeddings, complex deployment, slower inference
- Rejected: Infrastructure complexity and quality tradeoff not justified for 800-chunk dataset

**Why Gemini Won**: Free tier (1500 req/day) + good quality + simple API + smaller embeddings = optimal for hackathon constraints. Cost savings of $7.20/year vs OpenAI with acceptable quality tradeoff.

## References

- Feature Spec: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md)
- Implementation Plan: [specs/003-rag-chatbot/plan.md](../../specs/003-rag-chatbot/plan.md)
- Research Findings: [specs/003-rag-chatbot/research.md](../../specs/003-rag-chatbot/research.md) (Section 2: Gemini Embeddings + Streaming)
- Related ADRs: ADR-0007 (Data Storage - impacts Qdrant vector dimensions)
