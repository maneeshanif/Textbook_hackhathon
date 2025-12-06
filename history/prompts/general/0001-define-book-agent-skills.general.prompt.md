---
id: 0001
title: Define book agent skills
stage: general
date: 2025-12-06
surface: agent
model: GPT-5.1-Codex-Max (Preview)
feature: none
branch: unknown
user: user
command: none
labels: [book,rag,agents]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/agents/book-rag-agent.md
 - .claude/skills/skill.book-docusaurus.md
 - .claude/skills/skill.rag-chatbot.md
 - .claude/skills/skill.ui-embed.md
 - .claude/skills/skill.auth-personalization.md
 - .claude/skills/skill.localization-urdu.md
tests:
 - none
---

## Prompt

ok so ur first task is to go through the requirement.md file what tech is need and what we really want to make then see that how many skill needed for writing a book in docosaurus and so on also subagents ,, then u have to make those skills and agent in .claude folder pleaes follow the officail way how claudes code these think built up and then u have to give me the consititiotion commmadn for speckit and so on ...

## Response snapshot

Outlined required stack from requirements, drafted lead agent plus five supporting skills (book scaffold, RAG backend, UI embed, auth/personalization, Urdu localization), and noted next steps for constitution command and Spec-Kit flow.

## Outcome

- ✅ Impact: Added Claude agent+skills definitions aligned to book + RAG requirements and bonuses.
- 🧪 Tests: Not run (documentation-only change).
- 📁 Files: New agent file and five skill files under `.claude/`.
- 🔁 Next prompts: Provide constitution command usage; optionally run Spec-Kit spec/plan/tasks; begin implementation.
- 🧠 Reflection: Need to formalize feature spec/plan with `/sp.specify`/`/sp.plan` before coding.

## Evaluation notes (flywheel)

- Failure modes observed: None yet (planning docs only).
- Graders run and results (PASS/FAIL): None.
- Prompt variant (if applicable): n/a.
- Next experiment (smallest change to try): Start constitution/spec flow to lock principles and plan build tasks.
