# ADR-0004: Custom Component Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-06
- **Feature:** 001-docusaurus-book
- **Context:** The textbook requires custom React components for interactive features: DifficultyBadge (content level indicators), ChatbotPlaceholder (Phase 2 AI assistant stub), and ChapterHeader (metadata display). These components must be available in all MDX files without explicit imports, support both themes, and meet WCAG 2.1 AA accessibility standards.

## Decision

We will use a global MDX component registration pattern with the following architecture:

- **Registration Method**: Theme swizzling via `@theme/MDXComponents`
- **Component Location**: `src/components/[ComponentName]/index.tsx`
- **Styling Approach**: CSS Modules (`styles.module.css`) per component
- **Type Safety**: TypeScript interfaces defined in `specs/contracts/` as source of truth
- **Accessibility**: ARIA labels, keyboard navigation, focus indicators in all components
- **Theme Support**: CSS variables from Docusaurus Infima (e.g., `var(--ifm-color-primary)`)

Global registration:
```typescript
// src/theme/MDXComponents.tsx
import MDXComponents from '@theme-original/MDXComponents';
import DifficultyBadge from '@site/src/components/DifficultyBadge';
import ChatbotPlaceholder from '@site/src/components/ChatbotPlaceholder';
import ChapterHeader from '@site/src/components/ChapterHeader';

export default {
  ...MDXComponents,
  DifficultyBadge,
  ChatbotPlaceholder,
  ChapterHeader,
};
```

Usage in MDX (no imports needed):
```mdx
<DifficultyBadge level="beginner" />
<ChatbotPlaceholder position="bottom-right" />
```

## Consequences

### Positive

- Clean MDX files without import boilerplate
- Consistent component API enforced by TypeScript contracts
- CSS Modules prevent style leakage between components
- Theme variables ensure automatic dark/light mode support
- Accessibility patterns centralized and reusable
- Components testable in isolation with Jest/Testing Library
- Contract-first development enables parallel implementation

### Negative

- Theme swizzling creates coupling to Docusaurus internals
- Global registration may cause naming conflicts with future components
- CSS Modules less flexible than styled-components for dynamic styling
- Component changes require rebuild (no hot module replacement for theme files)
- Learning curve for contributors unfamiliar with Docusaurus theming

## Alternatives Considered

**Alternative A: Per-file MDX imports**
- Pros: Explicit dependencies, no theme swizzling needed
- Cons: Repetitive imports in every MDX file, easy to forget
- Rejected: Global registration is DRY and less error-prone

**Alternative B: MDX plugins (remark/rehype)**
- Pros: Transform at build time, no runtime overhead
- Cons: Complex to write and debug, limited to static transformations
- Rejected: React components provide better interactivity and maintainability

**Alternative C: Web Components**
- Pros: Framework-agnostic, native browser support
- Cons: Poor React integration, no TypeScript type checking, SSR complexity
- Rejected: React components integrate seamlessly with Docusaurus

**Alternative D: Tailwind CSS instead of CSS Modules**
- Pros: Utility-first, fast prototyping, consistent design system
- Cons: Additional build setup, conflicts with Infima, larger bundle
- Rejected: CSS Modules align with Docusaurus conventions and use Infima variables

## References

- Feature Spec: [specs/001-docusaurus-book/spec.md](../specs/001-docusaurus-book/spec.md) - FR-010, FR-013
- Implementation Plan: [specs/001-docusaurus-book/plan.md](../specs/001-docusaurus-book/plan.md)
- Contracts: [specs/001-docusaurus-book/contracts/](../specs/001-docusaurus-book/contracts/)
- Related ADRs: ADR-0001 (Framework Stack)
- Context7 Research: [specs/001-docusaurus-book/research.md](../specs/001-docusaurus-book/research.md) - Section 3 (Custom MDX Components)
