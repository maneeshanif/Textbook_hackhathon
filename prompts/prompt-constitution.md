# Physical AI & Humanoid Robotics Textbook - Constitution

> Project principles and non-negotiable rules for all agents (Claude Code, Copilot, and humans).

**Version:** 1.0.0  
**Last Updated:** 2025-01-20

---

## 1. Context7-First Development

**Principle:** NEVER generate code from memory. Always fetch the latest library documentation.

**Why:** Libraries update frequently. Stale knowledge causes broken code.

**Rules:**
- Before ANY code generation, call `mcp_upstash_conte_resolve-library-id` to find the library
- Then call `mcp_upstash_conte_get-library-docs` to fetch current docs
- If Context7 is unavailable, explicitly state "Unable to verify against latest docs"
- Document the Context7 lookup in the PHR (Prompt History Record)

**Libraries to always lookup:**
- `docusaurus` — Site configuration, MDX, plugins
- `react` — Components, hooks
- `fastapi` — Routes, dependencies, middleware
- `qdrant-client` — Vector operations
- `better-auth` — Authentication flows
- `openai` — Agents SDK, embeddings

---

## 2. Subagent Delegation

**Principle:** Use the right agent for the right job. The lead agent (CLAUDE.md) orchestrates.

**Why:** Specialized agents have focused skills and context. Better results, smaller diffs.

**Subagent Roster:**
| Agent | Domain | Skills |
|-------|--------|--------|
| `book-builder` | Docusaurus textbook | book-docusaurus, content-writer, chapter-formatting, visual-assets, accessibility-readability, ui-embed, localization-urdu |
| `rag-service` | Backend RAG system | rag-chatbot, ui-embed |
| `auth-personalization` | Auth & user prefs | auth-personalization, localization-urdu |
| `ops-release` | CI/CD & deployment | book-docusaurus, rag-chatbot |

**Rules:**
- Always check CLAUDE.md before starting work
- Delegate to appropriate subagent based on task domain
- If task spans multiple domains, coordinate between subagents
- Skills are in `.claude/skills/<skill-name>/SKILL.md`

---

## 3. Test-Driven Development (TDD)

**Principle:** Write tests first. Red → Green → Refactor.

**Why:** Tests are specifications. They prevent regressions and document behavior.

**Rules:**
- No feature is complete without tests
- Unit tests for all business logic
- Integration tests for API endpoints
- E2E tests for critical user flows
- Aim for 80%+ code coverage

**Testing Stack:**
- Python: `pytest`, `pytest-asyncio`, `httpx` for FastAPI
- React/TypeScript: `vitest`, `@testing-library/react`
- E2E: `playwright`

---

## 4. Security & Secrets

**Principle:** Never hardcode secrets. Never commit credentials.

**Why:** Security breaches destroy trust and projects.

**Rules:**
- All secrets in `.env` files (never committed)
- Use `.env.example` with placeholder values
- Validate environment variables at startup
- Use Better Auth for all authentication
- HTTPS everywhere (no HTTP in production)
- Sanitize all user input

**Required Environment Variables:**
```
OPENAI_API_KEY=sk-...
QDRANT_URL=https://...
QDRANT_API_KEY=...
NEON_DATABASE_URL=postgres://...
BETTER_AUTH_SECRET=...
```

---

## 5. Accessibility & Readability

**Principle:** Content must be accessible to learners of all levels.

**Why:** This is an educational textbook. Exclusion defeats the purpose.

**Rules:**
- Every concept explained at 3 levels:
  - 🟢 **Beginner:** Plain language, analogies
  - 🟡 **Intermediate:** Technical details
  - 🔴 **Advanced:** Deep dive, edge cases
- Use semantic HTML/MDX
- Alt text for all images
- Proper heading hierarchy (h1 → h2 → h3)
- Code blocks with syntax highlighting and comments
- Glossary terms linked throughout

---

## 6. Chapter Structure Standard

**Principle:** Consistent chapter formatting across the textbook.

**Why:** Predictable structure aids navigation and learning.

**Required Format:**
```markdown
---
sidebar_position: X
title: "X.Y Chapter Title"
description: "One-line description"
keywords: [keyword1, keyword2]
---

# X.Y Chapter Title

## Learning Objectives
- [ ] Objective 1
- [ ] Objective 2

## Content Sections (X.Y.1, X.Y.2, ...)

## Key Takeaways

## Exercises

## Further Reading
```

---

## 7. Smallest Viable Diff

**Principle:** Make the smallest change that solves the problem.

**Why:** Large changes are hard to review, test, and rollback.

**Rules:**
- One logical change per commit
- Don't refactor unrelated code
- If you see something to fix, create a separate issue/task
- PRs should be reviewable in < 15 minutes

---

## 8. Documentation as Code

**Principle:** Docs live with code. Update together.

**Why:** Outdated docs are worse than no docs.

**Rules:**
- README.md in every major directory
- Inline comments for non-obvious logic
- JSDoc/docstrings for all public functions
- API docs auto-generated from OpenAPI
- Architecture decisions in ADRs

---

## 9. Localization-Ready

**Principle:** Build for translation from day one.

**Why:** Urdu translation is a bonus point requirement (+50 points).

**Rules:**
- No hardcoded user-facing strings
- Use i18n framework from start
- RTL (right-to-left) support for Urdu
- Translation pipeline: Extract → Translate → Review → Integrate
- Maintain glossary of technical terms in both languages

---

## 10. Definition of Done

A feature is DONE when:

- [ ] Code compiles with no errors
- [ ] All tests pass (unit, integration, E2E)
- [ ] Code reviewed by at least one person (or AI agent)
- [ ] Documentation updated
- [ ] No security vulnerabilities (npm audit, pip-audit)
- [ ] Accessibility checked
- [ ] PHR created for the work
- [ ] Deployed to staging and verified

---

## Quick Reference Commands

```bash
# Spec-Kit Commands
/sp.constitution  # View/edit this constitution
/sp.spec <name>   # Create feature spec
/sp.plan <name>   # Create architecture plan
/sp.tasks <name>  # Create task breakdown
/sp.adr <title>   # Create Architecture Decision Record
/sp.phr           # Create Prompt History Record

# Development Commands
npm run dev       # Start Docusaurus dev server
uvicorn main:app --reload  # Start FastAPI server
pytest            # Run Python tests
npm test          # Run JS tests
```

---

## Agent Bootstrap Checklist

When starting a new session, every agent MUST:

1. ✅ Read `CLAUDE.md` for project context
2. ✅ Read this `constitution.md` for principles
3. ✅ Check `requirements.md` for scoring criteria
4. ✅ Identify which subagent should handle the task
5. ✅ Lookup libraries via Context7 before coding
6. ✅ Create PHR after completing work

---

*This constitution is the supreme law of this project. All agents and contributors must follow it.*
