# RAG Chatbot Backend

AI-powered Q&A chatbot backend for Physical AI textbook using RAG (Retrieval-Augmented Generation).

## Tech Stack

- **Framework**: FastAPI 0.109+ with async/await
- **Language**: Python 3.11+
- **Databases**:
  - Neon Serverless Postgres (chat history, user accounts)
  - Qdrant Cloud (vector embeddings for semantic search)
- **AI Service**: Google Gemini API
  - `text-embedding-004` for 768-dim embeddings
  - `gemini-2.0-flash-exp` for chat completions with streaming
- **Logging**: structlog with JSON formatting
- **Deployment**: Docker container on Railway/Render

## Prerequisites

- Python 3.11 or higher
- Neon Postgres database
- Qdrant Cloud account
- Google Gemini API key
- Better Auth instance (for authentication)

## Setup

### 1. Create Virtual Environment (using uv)

```bash
cd rag-chatbot-backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install all dependencies including dev tools
uv pip install -e ".[dev]"

# Or just production dependencies
uv pip install -e .
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 4. Run Database Migrations

```bash
# Run SQL migrations against Neon database
# TODO: Add migration runner script
```

### 5. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

## Project Structure

```
rag-chatbot-backend/
├── app/
│   ├── api/          # API route handlers
│   ├── models/       # Pydantic schemas
│   ├── services/     # Business logic (RAG, ingestion, etc.)
│   ├── middleware/   # FastAPI middleware (logging, auth, rate limiting)
│   ├── config.py     # Configuration loading
│   ├── database.py   # Postgres connection pool
│   ├── qdrant_client.py  # Qdrant async client wrapper
│   ├── gemini_client.py  # Gemini API client
│   └── main.py       # FastAPI app initialization
├── migrations/       # SQL schema migrations
├── scripts/          # Utility scripts (ingestion, cleanup, etc.)
├── tests/            # pytest tests
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/chat/query` - Submit question, get streamed response
- `POST /api/chat/query-selection` - Query with selected text context
- `GET /api/chat/history` - Retrieve chat history
- `POST /api/chat/migrate` - Migrate localStorage sessions to database
- `POST /api/chat/feedback` - Submit feedback (thumbs up/down)
- `GET /api/admin/metrics` - Admin metrics dashboard

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
ruff format app/ scripts/

# Lint code
ruff check app/ scripts/

# Type checking
mypy app/
```

### Content Ingestion

```bash
# Ingest English textbook content
python scripts/ingest_textbook.py --language en --source ../book/docs

# Ingest Urdu textbook content
python scripts/ingest_textbook.py --language ur --source ../book/i18n/ur/docusaurus-plugin-content-docs/current
```

## Docker Deployment

### Build Image

```bash
docker build -t rag-chatbot-backend .
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env rag-chatbot-backend
```

### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

## Environment Variables

See `.env.example` for required configuration. Key variables:

- `NEON_CONNECTION_STRING` - Postgres connection string
- `QDRANT_URL` - Qdrant Cloud URL
- `QDRANT_API_KEY` - Qdrant API key
- `GEMINI_API_KEY` - Google Gemini API key
- `BETTER_AUTH_URL` - Better Auth instance URL
- `ADMIN_API_KEY` - Secure key for admin endpoints

## License

MIT
