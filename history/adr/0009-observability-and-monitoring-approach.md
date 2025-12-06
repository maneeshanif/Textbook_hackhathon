# ADR-0009: Observability and Monitoring Approach

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-06
- **Feature:** 003-rag-chatbot
- **Context:** Production chatbot requires debugging visibility without enterprise APM tools (Datadog, New Relic = $50+/month). Must trace failed queries end-to-end (user → vector search → LLM → response), monitor quality metrics (similarity scores, feedback ratings), and measure performance (latency percentiles). Hackathon timeline (5-7 days) cannot support complex observability infrastructure. Need cost-effective solution leveraging Railway/Render built-in log aggregation.

## Decision

We will use a lightweight structured logging + in-memory metrics approach:

- **Logging Framework**: structlog 24.1+ with JSON formatter
  - Format: Machine-readable JSON with fields: `timestamp`, `request_id`, `level`, `message`, `context`
  - Output: stdout (captured by Railway/Render dashboards automatically)
  - Log Levels: ERROR (failures), WARN (degraded perf), INFO (successful queries with metrics)
- **Request Tracing**: Unique request ID per request
  - Generation: UUID in FastAPI middleware at request entry
  - Propagation: Pass through all service layers (database, Qdrant, Gemini API)
  - Response Header: `X-Request-ID` in all API responses
  - Error Context: Include request_id in all error logs for traceback
- **Metrics Collection**: In-memory Python dict (not Prometheus/Grafana)
  - Query Volume: Total, per-user, per-hour counters
  - Latency: p50, p95, p99 percentiles using `collections.deque` (1000-sample rolling window)
  - Similarity Scores: Average, distribution, below-threshold count
  - Feedback: Positive rate calculation (thumbs up / total votes)
- **Admin Dashboard**: `/api/admin/metrics` endpoint (requires API key)
  - Returns JSON with aggregated stats
  - No visualization (consume with curl or Postman for hackathon)

## Consequences

### Positive

- Zero cost: No external APM services required ($600+/year savings)
- Structured JSON logs queryable with `grep`, `jq`, or Railway dashboard filters
- Request IDs enable end-to-end tracing without distributed tracing infrastructure (Jaeger/Zipkin)
- In-memory metrics ~10ms overhead per request (vs 50-100ms for Prometheus scraping)
- Railway/Render built-in log aggregation provides basic search and filtering
- Simple implementation: ~100 lines of middleware code (no complex agent installation)
- Admin metrics endpoint sufficient for daily review (manual monitoring acceptable for hackathon)

### Negative

- In-memory metrics lost on pod restart (no historical trending beyond Railway logs)
- No automatic alerting (must check /api/admin/metrics manually or with cron)
- No distributed tracing visualization (must correlate logs manually by request_id)
- Limited retention: Railway/Render logs typically 7-30 days max
- No real-time dashboards (Grafana/Kibana require separate infrastructure)
- Manual monitoring required (no PagerDuty/Opsgenie integration)
- Scaling limitations: In-memory metrics don't aggregate across multiple pods (each pod has separate stats)

## Alternatives Considered

**Alternative A: Prometheus + Grafana (Full Observability Stack)**
- Pros: Industry standard, beautiful dashboards, automatic alerting, historical metrics, distributed tracing support
- Cons: Requires separate infrastructure (2 additional services), setup complexity (~2 days), $10-20/month hosting, overkill for hackathon
- Rejected: Implementation time and cost not justified for 5-7 day project

**Alternative B: Datadog APM (Managed Observability)**
- Pros: Comprehensive monitoring, automatic instrumentation, excellent UX, distributed tracing, alerting
- Cons: Expensive ($31/host/month = $372/year), overkill for hackathon, vendor lock-in
- Rejected: Cost prohibitive for free-tier project

**Alternative C: Sentry (Error Tracking Only)**
- Pros: Excellent error tracking, free tier (5K events/month), easy integration, good Python support
- Cons: No performance monitoring (latency, throughput), no custom metrics, limited context
- Partially Adopted: Could add Sentry later for production error tracking (not in MVP scope)

**Alternative D: No Observability (Debug in Production)**
- Pros: Zero setup time, simplest approach
- Cons: No debugging visibility, impossible to diagnose failed queries, no quality metrics, unprofessional
- Rejected: Unacceptable for demo/evaluation, success criteria require metrics (SC-007: 75%+ positive feedback)

**Why Structured Logging + In-Memory Metrics Won**: Best balance of simplicity, cost, and hackathon timeline. Request IDs provide enough traceability for debugging without distributed tracing complexity.

## References

- Feature Spec: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md) (FR-026 to FR-028, Observability Clarification)
- Implementation Plan: [specs/003-rag-chatbot/plan.md](../../specs/003-rag-chatbot/plan.md) (Observability Strategy section, Phase 7)
- Research Findings: [specs/003-rag-chatbot/research.md](../../specs/003-rag-chatbot/research.md) (Section 7: Structured Logging)
- Related ADRs: ADR-0005 (Backend Stack - structlog integration with FastAPI)
