# Physical AI & Humanoid Robotics Textbook Constitution

## Core Principles

<!-- These rules are absolute: the agent follows them unconditionally. -->

### 1. Context7-First Development

**NEVER generate code from memory.** Before writing any code involving external libraries, ALWAYS:
1. Call `mcp_upstash_conte_resolve-library-id` to get the exact library ID
2. Call `mcp_upstash_conte_get-library-docs` to fetch current documentation
3. Only then generate code using the fetched documentation

**Required lookups before coding:**
- `docusaurus` for any site config, MDX, or React components
- `fastapi` for any backend routes or API development
- `qdrant-client` for vector store operations
- `better-auth` for authentication flows
- `openai` for AI/embedding features

### 2. Subagent Delegation

Route ALL implementation tasks to the appropriate subagent. Never implement directly.

| Domain | Subagent | Skills Used |
|--------|----------|-------------|
| Textbook content, MDX, chapters | `book-builder` | book-docusaurus, content-writer, chapter-formatting, visual-assets, accessibility-readability |
| RAG backend, embeddings, chat | `rag-service` | rag-chatbot, ui-embed |
| Auth, user prefs, sessions | `auth-personalization` | auth-personalization, localization-urdu |
| CI/CD, deployment, monitoring | `ops-release` | book-docusaurus, rag-chatbot |

### 3. Test-Driven Development (TDD)

Follow Red-Green-Refactor for ALL code:
- **RED**: Write failing test first (pytest for Python, Jest for React)
- **GREEN**: Minimum code to pass
- **REFACTOR**: Clean up while tests stay green

No PR merges without passing tests. Coverage target: 80%+.

### 4. Security Non-Negotiables

- **NEVER** hardcode secrets, tokens, or API keys
- **ALL** secrets go in `.env` files (gitignored)
- **Document** all required environment variables in README
- **Validate** all user inputs on both frontend and backend
- **Use** parameterized queries (SQLAlchemy/asyncpg) - NO raw SQL string concatenation

### 5. Accessibility First

All content must be accessible:
- **Semantic HTML** in all MDX components
- **ARIA labels** on interactive elements
- **Alt text** on all images and diagrams
- **Keyboard navigation** support
- **Multi-level explanations**: beginner → intermediate → advanced tracks

### 6. Chapter Structure Standard

All chapters follow the X.Y.Z numbering system:
```
X.0 - Chapter overview and learning objectives
X.1 - Core concept introduction
X.2-X.n - Topic sections
X.n+1 - Hands-on exercises
X.n+2 - Chapter summary and review
```

Required frontmatter for every MDX file:
```yaml
---
title: "Chapter X.Y: Title"
sidebar_position: Y
tags: [topic1, topic2]
difficulty: beginner|intermediate|advanced
estimated_time: "XX minutes"
---
```

### 7. Smallest Viable Diff

- Make the **minimum change** needed to satisfy the requirement
- **Do not** refactor unrelated code
- **Do not** add features not explicitly requested
- One PR = one logical change

### 8. Documentation as Code

- **README.md** in every major directory
- **JSDoc/docstrings** on all public functions
- **API contracts** defined before implementation
- **ADRs** for all architectural decisions

### 9. Localization-Ready

All user-facing text must support translation:
- Use translation keys, not hardcoded strings
- Urdu translation pipeline via `localization-urdu` skill
- RTL layout support in CSS

### 10. Definition of Done

A task is DONE only when:
- [ ] Code compiles/lints without errors
- [ ] All tests pass
- [ ] Code reviewed (or self-reviewed with checklist)
- [ ] Documentation updated
- [ ] Accessibility checked
- [ ] No console errors/warnings
- [ ] Works in both English and Urdu (if user-facing)

## Quick Reference Commands

| Command | Purpose |
|---------|---------|
| `/sp.spec <feature>` | Create feature specification |
| `/sp.plan` | Generate implementation plan |
| `/sp.tasks` | Break plan into testable tasks |
| `/sp.implement` | Execute tasks (Red-Green-Refactor) |
| `/sp.phr` | Record prompt history |
| `/sp.adr <title>` | Document architectural decision |

## Agent Bootstrap Checklist

When starting any task:
1. ✅ Read this constitution
2. ✅ Read CLAUDE.md for project context
3. ✅ Identify correct subagent for the task
4. ✅ Load relevant skills
5. ✅ Fetch library docs via Context7
6. ✅ Proceed with implementation

## Governance

- Constitution changes require explicit user approval
- ADRs document rationale for architectural decisions
- PHRs maintain complete history of all prompts
- Breaking changes to constitution increment major version

---

**Version**: 1.0.0 | **Ratified**: 2025-01-13 | **Last Amended**: 2025-01-13
