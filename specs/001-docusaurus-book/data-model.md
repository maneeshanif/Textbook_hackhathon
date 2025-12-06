# Data Model: Docusaurus Book Site

**Feature**: 001-docusaurus-book  
**Date**: 2025-12-06

## Entities

### Chapter

A major topic section containing multiple sub-sections.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `number` | integer | Chapter number (1, 2, 3...) | Required, >= 1 |
| `title` | string | Display title | Required, max 100 chars |
| `description` | string | Brief overview for index | Required, max 500 chars |
| `slug` | string | URL-friendly identifier | Auto-generated from title |
| `sections` | Section[] | Child sections | Min 1 section |
| `position` | integer | Order in sidebar | Auto from number |

**File Representation**: Folder (`docs/01-introduction/`) with `_category_.json`

```json
{
  "position": 1,
  "label": "Chapter 1: Introduction to Physical AI",
  "collapsible": true,
  "collapsed": false,
  "link": {
    "type": "generated-index",
    "title": "Chapter 1 Overview",
    "description": "An introduction to Physical AI concepts and terminology"
  }
}
```

---

### Section

A sub-topic within a chapter containing actual educational content.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `chapterNumber` | integer | Parent chapter | Required |
| `sectionNumber` | integer | Section number (0, 1, 2...) | Required, >= 0 |
| `title` | string | Section title | Required, max 100 chars |
| `difficulty` | enum | `beginner` \| `intermediate` \| `advanced` | Required |
| `estimatedTime` | string | Reading time | Required, format "XX minutes" |
| `tags` | string[] | Topic tags | Optional, max 5 |
| `content` | MDX | Educational content | Required |

**File Representation**: MDX file with frontmatter

```yaml
---
title: "1.1 What is Physical AI?"
sidebar_position: 1
tags: [physical-ai, definition, overview]
difficulty: beginner
estimated_time: "15 minutes"
---
```

**Section Types** (by `sectionNumber`):
- `X.0` - Chapter overview and learning objectives
- `X.1` - Core concept introduction
- `X.2-X.n` - Topic sections
- `X.n+1` - Hands-on exercises
- `X.n+2` - Chapter summary and review

---

### Exercise

A hands-on activity within a chapter.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `id` | string | Unique identifier | Auto-generated |
| `chapterNumber` | integer | Parent chapter | Required |
| `title` | string | Exercise title | Required |
| `instructions` | MDX | Step-by-step guide | Required |
| `difficulty` | enum | `beginner` \| `intermediate` \| `advanced` | Required |
| `estimatedTime` | string | Completion time | Required |
| `solution` | MDX | Optional solution | Collapsible |

**File Representation**: MDX within exercises section

```mdx
---
title: "1.3 Exercises"
sidebar_position: 3
difficulty: beginner
estimated_time: "30 minutes"
---

## Exercise 1.1: Identifying Physical AI

<DifficultyBadge level="beginner" />

**Instructions**: List three examples of Physical AI in everyday life...

<details>
<summary>Solution</summary>

1. Autonomous vacuum cleaners (Roomba)
2. Robotic arms in manufacturing
3. Self-driving car perception systems

</details>
```

---

### Translation

A localized version of content in a supported language.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `locale` | enum | `en` \| `ur` | Required |
| `pageId` | string | Original page identifier | Required |
| `content` | MDX | Translated content | Required |
| `status` | enum | `draft` \| `published` | Default: draft |
| `lastUpdated` | date | Translation update date | Auto |

**File Representation**: Mirror structure in i18n folder

```
i18n/
└── ur/
    └── docusaurus-plugin-content-docs/
        └── current/
            └── 01-introduction/
                └── 1.1-what-is-physical-ai.mdx  # Translated content
```

---

### DifficultyLevel (Enum)

| Value | Description | Color |
|-------|-------------|-------|
| `beginner` | Foundational concepts, no prerequisites | Green (#25c2a0) |
| `intermediate` | Builds on basics, some prior knowledge | Blue (#1877F2) |
| `advanced` | Technical deep-dive, requires expertise | Red (#fa383e) |

---

## Relationships

```
Chapter (1) ──────< (n) Section
    │
    └──────────────< (n) Exercise

Section (1) ──────< (n) Translation
```

- A **Chapter** contains 1 or more **Sections**
- A **Chapter** may have 0 or more **Exercises** (typically in X.n+1 section)
- A **Section** may have 0 or more **Translations** (1 per locale)

---

## State Transitions

### Translation Status

```
┌─────────┐     translate      ┌───────────┐
│  N/A    │ ─────────────────> │   draft   │
└─────────┘                    └───────────┘
                                     │
                                     │ review + approve
                                     ▼
                               ┌───────────┐
                               │ published │
                               └───────────┘
                                     │
                                     │ content updated
                                     ▼
                               ┌───────────┐
                               │   draft   │ (needs re-translation)
                               └───────────┘
```

---

## Data Volume Estimates

| Entity | Count (Phase 1) | Growth Rate |
|--------|-----------------|-------------|
| Chapters | 4 | +1-2 per month |
| Sections per Chapter | 5-6 | Stable |
| Total Pages | ~20 | +5-10 per month |
| Translations (Urdu) | 1 sample | +2-3 per month |
| Exercises per Chapter | 3-5 | Stable |

---

## Frontmatter Schema (TypeScript)

```typescript
interface SectionFrontmatter {
  title: string;                              // "1.1 What is Physical AI?"
  sidebar_position: number;                   // 1
  tags?: string[];                            // ["physical-ai", "definition"]
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimated_time: string;                     // "15 minutes"
  description?: string;                       // For SEO/index
  keywords?: string[];                        // For search
  hide_table_of_contents?: boolean;           // Default: false
  custom_edit_url?: string;                   // GitHub edit link
}

interface CategoryMetadata {
  position: number;
  label: string;
  collapsible?: boolean;                      // Default: true
  collapsed?: boolean;                        // Default: false
  className?: string;
  link?: {
    type: 'generated-index' | 'doc';
    title?: string;
    description?: string;
    slug?: string;
    id?: string;                              // For type: 'doc'
  };
  customProps?: Record<string, unknown>;
}
```
