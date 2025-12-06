# Physical AI & Humanoid Robotics Textbook

An interactive online textbook built with [Docusaurus](https://docusaurus.io/) covering physical AI, embodied intelligence, and humanoid robotics. Features multi-language support (English + Urdu with RTL), dark/light themes, and custom educational components.

## ✨ Features

- 📚 **Comprehensive Content**: 4 modules covering fundamentals to advanced topics
- 🌍 **Bilingual**: English and Urdu (اردو) with RTL layout support
- 🎨 **Theme Support**: Light and dark modes with smooth transitions
- 🧩 **Custom Components**:
  - `ChapterHeader` - Chapter metadata display
  - `DifficultyBadge` - Visual difficulty indicators
  - `ChatbotPlaceholder` - Coming soon AI assistant widget
- ♿ **Accessible**: WCAG 2.1 AA compliant with keyboard navigation
- 📱 **Responsive**: Mobile-first design
- 🔍 **Search**: Full-text search across all content
- 📊 **Math Support**: KaTeX for rendering equations

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
npm install
```

### Local Development

```bash
npm start
```

This command starts a local development server at `http://localhost:3000` and opens up a browser window. Most changes are reflected live without having to restart the server.

### Build

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

### Testing

```bash
# Run unit tests
npm test

# Run with coverage
npm run test:coverage
```

### Serve Production Build

```bash
npm run serve
```

### Type Checking

```bash
npm run typecheck
```

## 📁 Project Structure

```
book/
├── docs/                  # English content (MDX files)
├── i18n/ur/              # Urdu translations
├── src/
│   ├── components/       # Custom React components
│   ├── css/             # Global styles + RTL
│   ├── pages/           # Homepage and custom pages
│   └── theme/           # Docusaurus theme customizations
├── static/              # Static assets (images, etc.)
└── tests/               # Unit and E2E tests
```

## 🌍 Internationalization

Switch language using the dropdown in the navbar. Currently supported:
- **English** (default)
- **Urdu** (اردو) with RTL layout

## 📝 Adding Content

See [specs/001-docusaurus-book/quickstart.md](../specs/001-docusaurus-book/quickstart.md) for detailed content creation guide.

## 🧪 Testing

- **Unit tests**: `tests/unit/` - Component tests with Jest
- **E2E tests**: `tests/e2e/` - Navigation and accessibility tests with Playwright

## 📖 Documentation

- [Feature Specification](../specs/001-docusaurus-book/spec.md)
- [Implementation Plan](../specs/001-docusaurus-book/plan.md)
- [Developer Quickstart](../specs/001-docusaurus-book/quickstart.md)

## Deployment

Using SSH:

```bash
USE_SSH=true npm run deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> npm run deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
