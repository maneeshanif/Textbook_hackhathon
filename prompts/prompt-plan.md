# /sp.plan - Implementation Planning Command

Follow instructions in `.github/prompts/sp.plan.prompt.md`

---

## Feature Context

**Feature**: 001-docusaurus-book  
**Spec**: `specs/001-docusaurus-book/spec.md`  
**Branch**: `001-docusaurus-book`

## Technical Context (Pre-filled from Project Constitution)

Based on our constitution and requirements.md:

**Language/Version**: JavaScript/TypeScript (Node.js 18+)  
**Primary Dependencies**: Docusaurus 3.x, React 18, MDX 3  
**Storage**: N/A (static site, no database in Phase 1)  
**Testing**: Jest for unit tests, Playwright for E2E  
**Target Platform**: Web (GitHub Pages / Vercel deployment)  
**Project Type**: Web application (documentation/book site)  
**Performance Goals**: Page load < 3 seconds, Lighthouse 90+  
**Constraints**: Mobile responsive (320px+), Accessibility WCAG 2.1 AA  
**Scale/Scope**: ~4 chapters, ~20 pages, 2 languages (EN/UR)

## Constitution Gates to Verify

From `.specify/memory/constitution.md`:

1. ✅ **Context7-First**: Must fetch Docusaurus docs before implementation
2. ✅ **Subagent Delegation**: Route to `book-builder` agent
3. ✅ **TDD**: Jest tests for components, Playwright for navigation
4. ✅ **Security**: No secrets (static site)
5. ✅ **Accessibility**: ARIA, semantic HTML, alt text
6. ✅ **Chapter Structure**: X.Y.Z numbering per constitution
7. ✅ **Smallest Diff**: Scaffold structure only, content later
8. ✅ **Docs as Code**: README in each directory
9. ✅ **Localization-Ready**: i18n configured from start
10. ✅ **Definition of Done**: Checklist per PR

## Phase 0: Research Topics

Research needed before implementation:

1. **Docusaurus 3.x i18n Setup**
   - How to configure multi-language support
   - RTL layout for Urdu
   - Translation file structure

2. **Docusaurus Sidebar Configuration**
   - Auto-generation from folder structure
   - Chapter numbering (X.Y.Z) in sidebar
   - Category metadata

3. **MDX Component Patterns**
   - Difficulty level indicator component
   - Chatbot placeholder component
   - Accessible code blocks

4. **Theme Customization**
   - Dark/light mode persistence
   - Custom CSS for RTL support
   - Mobile responsive breakpoints

## Phase 1: Design Artifacts to Generate

### 1. Project Structure (`/book/` directory)

```
book/
├── docusaurus.config.js    # Main config with i18n
├── sidebars.js             # Auto-generated sidebar config
├── package.json            # Dependencies
├── src/
│   ├── components/         # Reusable MDX components
│   │   ├── DifficultyBadge/
│   │   ├── ChatbotPlaceholder/
│   │   └── CodeBlock/
│   ├── css/
│   │   ├── custom.css      # Theme overrides
│   │   └── rtl.css         # RTL styles for Urdu
│   └── pages/
│       └── index.js        # Homepage
├── docs/                   # English content
│   ├── 01-introduction/
│   │   ├── 1.0-overview.mdx
│   │   ├── 1.1-what-is-physical-ai.mdx
│   │   └── _category_.json
│   ├── 02-humanoid-robotics/
│   ├── 03-sensors-actuators/
│   └── 04-ai-integration/
├── i18n/
│   └── ur/                 # Urdu translations
│       ├── docusaurus-theme-classic/
│       └── docs/           # Translated content
└── static/
    └── img/                # Images and diagrams
```

### 2. Data Model (`data-model.md`)

Entities from spec:
- **Chapter**: id, number (X), title, description, sections[]
- **Section**: id, number (X.Y), title, difficulty, estimatedTime, content
- **Exercise**: id, chapterId, title, instructions, solution
- **Translation**: locale, pageId, content, status (draft/published)

### 3. Component Contracts (`contracts/`)

- `DifficultyBadge.tsx` - Props: level (beginner|intermediate|advanced)
- `ChatbotPlaceholder.tsx` - Props: position, onExpand callback
- `ChapterHeader.tsx` - Props: number, title, estimatedTime, difficulty

### 4. Quickstart Guide (`quickstart.md`)

How to:
1. Clone and install dependencies
2. Run locally (`npm start`)
3. Add a new chapter
4. Add Urdu translation
5. Build for production

## Expected Outputs

After `/sp.plan` completes:

```
specs/001-docusaurus-book/
├── spec.md           # (existing)
├── plan.md           # Implementation plan
├── research.md       # Context7 findings for Docusaurus
├── data-model.md     # Chapter/Section/Exercise entities
├── quickstart.md     # Developer setup guide
└── contracts/        # Component interfaces
    ├── DifficultyBadge.ts
    ├── ChatbotPlaceholder.ts
    └── ChapterHeader.ts
```

## Notes for Agent

- **MUST use Context7** to fetch latest Docusaurus 3.x documentation before generating any config
- Delegate to `book-builder` subagent for implementation
- Load skills: `book-docusaurus`, `chapter-formatting`, `accessibility-readability`, `localization-urdu`
- Follow constitution's X.Y.Z chapter structure strictly
