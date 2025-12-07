# ChatWidget Component

A fully-featured RAG-powered chat widget for the Docusaurus textbook, providing real-time AI assistance with streaming responses and chapter citations.

## Features

- 🚀 **Streaming Responses**: Real-time SSE (Server-Sent Events) for smooth chat experience
- 📚 **Smart Citations**: Automatically links relevant textbook chapters
- 🌐 **Bilingual Support**: English and Urdu language switching
- 💾 **Session Persistence**: Chat history maintained via localStorage
- 🎨 **Dark Mode**: Full theme support with Docusaurus
- 📱 **Responsive Design**: Mobile-optimized floating widget
- ⚡ **Performance**: Optimized with React hooks and lazy loading

## Architecture

```
ChatWidget/
├── ChatWidget.tsx              # Main component with state management
├── ChatWidget.module.css       # Widget styling
├── index.ts                    # Public exports
├── types/
│   └── index.ts               # TypeScript interfaces
├── components/
│   ├── Message.tsx            # Individual message bubble
│   ├── Message.module.css
│   ├── MessageList.tsx        # Scrollable message container
│   ├── MessageList.module.css
│   ├── InputBox.tsx           # Text input with send button
│   └── InputBox.module.css
├── hooks/
│   └── useStreamingQuery.ts   # SSE streaming hook
└── utils/
    └── session.ts             # localStorage session management
```

## Usage

The widget is automatically integrated via Docusaurus's Root wrapper:

```tsx
// src/theme/Root.tsx
import { ChatWidget } from '../components/ChatWidget';

export default function Root({ children }) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
```

## Configuration

**⚠️ Important**: The API URL is currently hardcoded in the hook for simplicity.

To change the backend API URL, edit `hooks/useStreamingQuery.ts`:

```typescript
// Development
const API_BASE_URL = 'http://localhost:8000';

// Production (update before deployment)
const API_BASE_URL = 'https://api.yourdomain.com';
```

**Note**: This avoids Webpack configuration complexity in Docusaurus. For a more dynamic solution, you can implement environment-based configuration using Docusaurus's `customFields` in `docusaurus.config.ts`.

## Component API

### ChatWidget

Main floating widget component (no props required).

**State Management:**
- `messages`: Array of chat messages
- `sessionToken`: Unique session identifier
- `language`: Current language (`'en'` | `'ur'`)
- `isOpen`: Widget visibility

**Key Methods:**
- `handleSendMessage(content: string)`: Send user query
- `handleClearHistory()`: Reset chat and session
- `handleLanguageChange(language: string)`: Switch language
- `handleCitationClick(url: string)`: Navigate to chapter

### useStreamingQuery Hook

```tsx
const { 
  sendQuery, 
  isLoading, 
  error, 
  currentMessage, 
  citations 
} = useStreamingQuery(language, onMessageComplete);
```

**Parameters:**
- `language`: Target language for responses
- `onMessageComplete`: Callback when streaming finishes

**Returns:**
- `sendQuery(query, sessionToken?, selectedText?)`: Initiate query
- `isLoading`: Loading state
- `error`: Error message (if any)
- `currentMessage`: Current streaming text
- `citations`: Array of chapter citations

## Styling

The widget uses CSS modules with Docusaurus theme variables:

```css
/* Uses Docusaurus theme variables */
var(--ifm-color-primary)
var(--ifm-background-color)
var(--ifm-color-emphasis-300)
```

**Custom Properties:**
- Floating button: 60x60px, bottom-right corner
- Chat panel: 400x600px (mobile: fullscreen)
- Z-index: 999 (button), 1000 (panel)

## Session Management

Sessions are stored in `localStorage`:

```typescript
// Keys
'rag_chat_session_token'  // Session identifier
'rag_chat_language'       // Current language preference

// Methods
getSessionToken(): string | null
setSessionToken(token: string): void
clearSessionToken(): void
getSessionLanguage(): string
setSessionLanguage(language: string): void
```

## SSE Protocol

The widget communicates with the backend via Server-Sent Events:

**Request:**
```json
POST /api/chat/query
{
  "query": "What is forward kinematics?",
  "session_token": "1234567890-abc123",
  "language": "en",
  "selected_text": null
}
```

**Response Stream:**
```
data: {"chunk": "Forward"}
data: {"chunk": " kinematics"}
data: {"done": true, "message_id": "msg_123", "citations": [...]}
```

## Error Handling

The widget handles:
- Network failures (connection lost)
- Backend errors (4xx, 5xx)
- SSE parsing errors
- Session expiration

Errors display in a dismissible banner at the top of the chat panel.

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support (Enter to send, Shift+Enter for newline)
- Focus management for modal behavior
- Screen reader-friendly message structure

## Performance

- Lazy message rendering with virtual scrolling
- Debounced auto-scroll on new messages
- CSS animations with `transform` (GPU-accelerated)
- Event listener cleanup on unmount

## Browser Support

- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+
- Mobile Safari: 14+
- Chrome Android: 90+

Requires:
- ES2020+ features
- Fetch API
- EventSource (SSE)
- localStorage

## Testing

```bash
# Unit tests
npm test -- ChatWidget

# Specific component
npm test -- Message.test.tsx

# With coverage
npm test:coverage -- ChatWidget
```

## Development

```bash
# Start Docusaurus dev server
npm start

# Start backend (in separate terminal)
cd ../rag-chatbot-backend
uv run uvicorn app.main:app --reload

# Widget appears at bottom-right corner
# Open http://localhost:3000
```

## Troubleshooting

### Widget doesn't appear
- Check `src/theme/Root.tsx` exists and imports ChatWidget
- Verify no console errors
- Clear `.docusaurus` cache: `npm run clear`

### SSE connection fails
- Ensure backend is running on `http://localhost:8000`
- Check CORS is enabled in backend
- Verify `.env.local` has correct `REACT_APP_API_URL`

### Citations not working
- Backend must return `citations` array in final SSE message
- URLs must be valid Docusaurus routes (e.g., `/docs/chapter-id`)

### Language switching clears history
- Expected behavior - sessions are language-specific
- To preserve history, implement backend session migration

## Future Enhancements

- [ ] Text selection queries (highlight text → ask about it)
- [ ] Voice input support
- [ ] Export chat history
- [ ] Feedback ratings (thumbs up/down)
- [ ] Typing indicators
- [ ] Read receipts
- [ ] Multi-modal responses (images, code blocks)
- [ ] Context awareness (current chapter)

## Related Files

- Backend API: `../rag-chatbot-backend/app/api/chat.py`
- RAG Service: `../rag-chatbot-backend/app/services/rag.py`
- Tasks: `../specs/003-rag-chatbot/tasks.md`
- ADRs: `../history/adr/0008-authentication-and-session-management-strategy.md`
