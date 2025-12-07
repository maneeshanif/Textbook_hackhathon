# RAG Chatbot - Quick Start Guide

Complete setup guide for running the full-stack RAG chatbot (backend + frontend).

## Prerequisites

- **Python 3.11+** with `uv` package manager
- **Node.js 18+** with npm
- **PostgreSQL** (Neon Serverless)
- **Qdrant Cloud** account
- **Google Gemini API** key

## Backend Setup

### 1. Install Dependencies

```bash
cd rag-chatbot-backend
uv sync
```

### 2. Configure Environment

Create `.env` file:

```bash
# Database
NEON_CONNECTION_STRING=postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require

# Vector Database
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# AI Service
GEMINI_API_KEY=your_gemini_api_key

# Admin
ADMIN_API_KEY=your_admin_key

# CORS (add frontend URL)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Optional
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Run Database Migrations

```bash
uv run ./scripts/run_migrations.py
```

Expected output:
```
Running migration 001_create_users.sql...
Running migration 002_create_sessions.sql...
Running migration 003_create_messages.sql...
Running migration 004_create_feedback.sql...
All migrations completed successfully!
```

### 4. Ingest Textbook Content

```bash
# English content
uv run ./scripts/ingest_textbook.py --language en --create-collection

# Urdu content (if available)
uv run ./scripts/ingest_textbook.py --language ur --create-collection
```

### 5. Start Backend Server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify at: http://localhost:8000/api/health

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "postgres": true,
    "qdrant": true,
    "gemini": true
  }
}
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd ../book
npm install
```

### 2. Configure Environment

Create `.env.local`:

```bash
REACT_APP_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm start
```

Opens at: http://localhost:3000

## Verification

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/health
```

### 2. Test Chat Query

```bash
curl -N -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is forward kinematics?",
    "language": "en"
  }'
```

### 3. Test Frontend Widget

1. Open http://localhost:3000
2. Click floating chat button (bottom-right)
3. Type: "What is forward kinematics?"
4. Press Enter or click Send
5. Watch streaming response with citations

## Troubleshooting

### Backend Issues

**Connection refused:**
```bash
# Check if backend is running
ps aux | grep uvicorn

# Restart backend
cd rag-chatbot-backend
uv run uvicorn app.main:app --reload
```

**Database errors:**
```bash
# Re-run migrations
uv run ./scripts/run_migrations.py

# Check connection string
echo $NEON_CONNECTION_STRING
```

**Qdrant/Gemini unhealthy:**
```bash
# Verify API keys in .env
cat .env | grep -E "QDRANT_API_KEY|GEMINI_API_KEY"

# Test Qdrant connection
curl -H "api-key: $QDRANT_API_KEY" $QDRANT_URL/collections
```

### Frontend Issues

**Widget not appearing:**
```bash
# Clear Docusaurus cache
npm run clear

# Rebuild
npm start
```

**CORS errors in browser console:**
```bash
# Add frontend URL to backend CORS_ORIGINS
# In rag-chatbot-backend/.env:
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Restart backend
```

**SSE connection fails:**
```bash
# Check .env.local
cat .env.local

# Should show:
REACT_APP_API_URL=http://localhost:8000
```

### Network Issues

**Can't connect from browser:**
```bash
# Check firewall
sudo ufw status

# Allow port 8000
sudo ufw allow 8000

# Check if backend is listening
netstat -tlnp | grep 8000
```

## Production Deployment

### Backend (Railway/Render)

1. Set environment variables
2. Run migrations on startup:
   ```bash
   python scripts/run_migrations.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. Update CORS_ORIGINS with frontend domain

### Frontend (Vercel/Netlify)

1. Set build command: `npm run build`
2. Set output directory: `build`
3. Add environment variable:
   ```
   REACT_APP_API_URL=https://your-backend-domain.com
   ```

### Environment Variables

**Backend `.env`:**
```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
CORS_ORIGINS=https://your-frontend-domain.com
NEON_CONNECTION_STRING=postgresql://...
QDRANT_URL=https://...
QDRANT_API_KEY=...
GEMINI_API_KEY=...
ADMIN_API_KEY=...
```

**Frontend `.env.production`:**
```bash
REACT_APP_API_URL=https://your-backend-domain.com
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Docusaurus (http://localhost:3000)                │     │
│  │  └─ ChatWidget Component                           │     │
│  │     ├─ useStreamingQuery hook (SSE)                │     │
│  │     ├─ MessageList                                 │     │
│  │     └─ InputBox                                    │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP POST /api/chat/query
                        │ Server-Sent Events (SSE)
┌───────────────────────▼─────────────────────────────────────┐
│                     Backend API                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  FastAPI (http://localhost:8000)                   │     │
│  │  └─ /api/chat/query endpoint                       │     │
│  │     ├─ RAG Service                                 │     │
│  │     │  ├─ Vector Search (Qdrant)                   │     │
│  │     │  └─ Streaming Chat (Gemini)                  │     │
│  │     └─ Database (Neon Postgres)                    │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Test all features:**
   - [ ] English queries
   - [ ] Urdu queries  
   - [ ] Language switching
   - [ ] Citation links
   - [ ] Clear history

2. **Implement Phase 4 features:**
   - [ ] Text selection queries
   - [ ] Context-aware suggestions

3. **Add monitoring:**
   - [ ] Error tracking (Sentry)
   - [ ] Analytics (PostHog)
   - [ ] Performance monitoring

4. **Optimize performance:**
   - [ ] Response caching
   - [ ] Rate limiting
   - [ ] Load testing

## Resources

- Backend docs: `rag-chatbot-backend/README.md`
- Technical overview: `rag-chatbot-backend/TECHNICAL_OVERVIEW.md`
- Widget docs: `book/src/components/ChatWidget/README.md`
- Tasks: `specs/003-rag-chatbot/tasks.md`
- ADRs: `history/adr/`

## Support

For issues:
1. Check troubleshooting section above
2. Review backend logs: `tail -f rag-chatbot-backend/logs/*.log`
3. Check browser console for frontend errors
4. Verify all environment variables are set
