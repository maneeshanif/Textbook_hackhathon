# Quickstart: Docusaurus Book Site

**Feature**: 001-docusaurus-book  
**Date**: 2025-12-06

## Prerequisites

- Node.js 18+ (LTS recommended)
- npm 9+ or yarn 1.22+
- Git

## 1. Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd day-2

# Switch to feature branch
git checkout 001-docusaurus-book

# Navigate to book directory
cd book

# Install dependencies
npm install
```

## 2. Run Locally

```bash
# Start development server
npm start

# Site will be available at http://localhost:3000
```

The development server supports hot reload - changes to MDX files reflect immediately.

## 3. Add a New Chapter

### Step 1: Create Chapter Folder

```bash
mkdir -p docs/05-new-topic
```

### Step 2: Add Category Metadata

Create `docs/05-new-topic/_category_.json`:

```json
{
  "position": 5,
  "label": "Chapter 5: New Topic",
  "collapsible": true,
  "collapsed": false,
  "link": {
    "type": "generated-index",
    "title": "Chapter 5 Overview",
    "description": "Description of this chapter"
  }
}
```

### Step 3: Create Chapter Sections

Create `docs/05-new-topic/5.0-overview.mdx`:

```mdx
---
title: "5.0 Chapter Overview"
sidebar_position: 0
tags: [new-topic]
difficulty: beginner
estimated_time: "5 minutes"
---

# Chapter 5: New Topic

<DifficultyBadge level="beginner" />

## Learning Objectives

By the end of this chapter, you will:

- Understand concept A
- Be able to apply technique B
- Know when to use approach C
```

Create additional sections following the X.Y pattern:
- `5.1-concept-intro.mdx`
- `5.2-topic-section.mdx`
- `5.3-exercises.mdx`
- `5.4-summary.mdx`

## 4. Add Urdu Translation

### Step 1: Generate Translation Files

```bash
# Generate translation JSON files
npm run write-translations -- --locale ur
```

### Step 2: Translate UI Strings

Edit `i18n/ur/docusaurus-theme-classic/navbar.json`:

```json
{
  "title": {
    "message": "فزیکل اے آئی ٹیکسٹ بک",
    "description": "The title in the navbar"
  }
}
```

### Step 3: Translate Content

Copy the MDX file to the translation directory:

```bash
mkdir -p i18n/ur/docusaurus-plugin-content-docs/current/01-introduction
cp docs/01-introduction/1.0-overview.mdx \
   i18n/ur/docusaurus-plugin-content-docs/current/01-introduction/
```

Edit the copied file with Urdu content.

### Step 4: Preview Translation

```bash
# Start dev server with Urdu locale
npm start -- --locale ur
```

## 5. Create Custom Component

### Step 1: Create Component File

Create `src/components/MyComponent/index.tsx`:

```tsx
import React from 'react';
import styles from './styles.module.css';

interface Props {
  title: string;
  children: React.ReactNode;
}

export default function MyComponent({ title, children }: Props) {
  return (
    <div className={styles.container}>
      <h3>{title}</h3>
      {children}
    </div>
  );
}
```

### Step 2: Add Styles

Create `src/components/MyComponent/styles.module.css`:

```css
.container {
  border: 1px solid var(--ifm-color-primary);
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}
```

### Step 3: Register Globally (Optional)

Add to `src/theme/MDXComponents.tsx`:

```tsx
import MyComponent from '@site/src/components/MyComponent';

export default {
  ...MDXComponents,
  MyComponent,
};
```

### Step 4: Use in MDX

```mdx
<MyComponent title="Important Note">
  This is the content inside the component.
</MyComponent>
```

## 6. Build for Production

```bash
# Build static files
npm run build

# Preview production build
npm run serve
```

Output will be in the `build/` directory.

## 7. Common Commands

| Command | Description |
|---------|-------------|
| `npm start` | Start dev server (English) |
| `npm start -- --locale ur` | Start dev server (Urdu) |
| `npm run build` | Build production site |
| `npm run serve` | Preview production build |
| `npm run write-translations -- --locale ur` | Generate Urdu translation files |
| `npm run clear` | Clear cache |
| `npm run swizzle` | Customize theme components |

## 8. Troubleshooting

### Build Fails with MDX Error

Check that all MDX files have valid frontmatter:

```yaml
---
title: "Required"
sidebar_position: 1
difficulty: beginner
estimated_time: "10 minutes"
---
```

### i18n Not Working

1. Ensure locale is in `docusaurus.config.js`:
   ```javascript
   i18n: {
     locales: ['en', 'ur'],
   }
   ```

2. Translation files exist in `i18n/ur/`

### Component Not Found

1. Check import path uses `@site/` alias
2. If using global registration, restart dev server

### RTL Layout Issues

Ensure Urdu locale has `direction: 'rtl'` in config:

```javascript
localeConfigs: {
  ur: {
    direction: 'rtl',
  },
}
```

## Directory Structure Reference

```
book/
├── docs/                    # English content
│   ├── 01-introduction/
│   │   ├── _category_.json
│   │   ├── 1.0-overview.mdx
│   │   └── ...
│   └── ...
├── i18n/                    # Translations
│   └── ur/
│       ├── docusaurus-theme-classic/
│       └── docusaurus-plugin-content-docs/
├── src/
│   ├── components/          # Custom components
│   ├── css/                 # Custom styles
│   ├── pages/               # Standalone pages
│   └── theme/               # Theme overrides
├── static/                  # Static assets
├── docusaurus.config.js     # Main config
├── sidebars.js              # Sidebar config
└── package.json
```
