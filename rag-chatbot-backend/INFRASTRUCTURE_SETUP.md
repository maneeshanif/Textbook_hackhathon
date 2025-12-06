# Infrastructure Setup Guide

This document provides step-by-step instructions for setting up the external infrastructure required for the RAG Chatbot.

## Overview

The chatbot requires the following external services:
1. **Neon Postgres** - Relational database for chat history and user accounts
2. **Qdrant Cloud** - Vector database for semantic search over textbook content
3. **Google Gemini API** - AI service for embeddings and chat completions
4. **Better Auth** (Optional) - Authentication service for user management
5. **Railway/Render** - Deployment platform for backend API

---

## Task T009: Create Neon Postgres Database

### 1. Sign up for Neon

Visit [https://neon.tech](https://neon.tech) and create a free account.

### 2. Create a New Project

- Click "New Project"
- Project name: `rag-chatbot`
- Region: Choose closest to your users
- Postgres version: 16 (recommended)

### 3. Get Connection String

After project creation, copy the connection string from the dashboard:

```
postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 4. Add to .env

```bash
cd rag-chatbot-backend
cp .env.example .env
# Add the connection string:
NEON_CONNECTION_STRING=postgresql://user:password@...
```

### 5. Verify Connection

```bash
# Test connection (requires psql)
psql "your_connection_string_here" -c "SELECT version();"
```

**Free Tier Limits**: 512 MB storage, 0.5 GB data transfer/month

---

## Task T010: Create Qdrant Cloud Collection (English)

### 1. Sign up for Qdrant Cloud

Visit [https://cloud.qdrant.io](https://cloud.qdrant.io) and create a free account.

### 2. Create a Cluster

- Click "Create Cluster"
- Cluster name: `rag-chatbot-cluster`
- Region: Choose closest to your users
- Plan: Free tier (1 GB storage)

### 3. Get API Credentials

- After cluster creation, go to "API Keys"
- Create a new API key and copy it
- Copy the cluster URL (e.g., `https://xyz.qdrant.io`)

### 4. Create English Collection

Using Qdrant Cloud dashboard or API:

```python
# Using Python client (after setup)
from qdrant_client import QdrantClient

client = QdrantClient(
    url="YOUR_QDRANT_URL",
    api_key="YOUR_API_KEY"
)

client.create_collection(
    collection_name="textbook_chunks_en",
    vectors_config={
        "size": 768,  # Gemini text-embedding-004 dimension
        "distance": "Cosine"
    }
)
```

Or via REST API:

```bash
curl -X PUT 'https://xyz.qdrant.io/collections/textbook_chunks_en' \
  -H 'api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "vectors": {
      "size": 768,
      "distance": "Cosine"
    }
  }'
```

### 5. Add to .env

```bash
QDRANT_URL=https://xyz.qdrant.io
QDRANT_API_KEY=your_api_key_here
```

---

## Task T011: Create Qdrant Cloud Collection (Urdu) [Parallel]

Follow the same process as T010, but create a second collection:

```python
client.create_collection(
    collection_name="textbook_chunks_ur",
    vectors_config={
        "size": 768,
        "distance": "Cosine"
    }
)
```

Or via REST API:

```bash
curl -X PUT 'https://xyz.qdrant.io/collections/textbook_chunks_ur' \
  -H 'api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "vectors": {
      "size": 768,
      "distance": "Cosine"
    }
  }'
```

**Free Tier Limits**: 1 GB total storage (shared between both collections)

---

## Task T012: Obtain Gemini API Key [Parallel]

### 1. Go to Google AI Studio

Visit [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

### 2. Create API Key

- Sign in with your Google account
- Click "Create API Key"
- Copy the generated key

### 3. Add to .env

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Verify API Access

```bash
# Test API call
curl -X POST \
  'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

**Free Tier Limits**: 1,500 requests per day

---

## Task T013: Setup Railway/Render Account [Parallel]

### Option A: Railway (Recommended)

#### 1. Sign up for Railway

Visit [https://railway.app](https://railway.app) and sign up with GitHub.

#### 2. Create New Project

- Click "New Project"
- Select "Empty Project"
- Project name: `rag-chatbot-backend`

#### 3. Install Railway CLI (optional, for deployment)

```bash
npm install -g @railway/cli
railway login
```

#### 4. Link Project

```bash
cd rag-chatbot-backend
railway link
```

**Free Tier Limits**: $5 credit (500 hours/month), 512 MB RAM, 1 GB disk

### Option B: Render

#### 1. Sign up for Render

Visit [https://render.com](https://render.com) and sign up with GitHub.

#### 2. Create New Web Service

- Click "New +" → "Web Service"
- Connect your GitHub repository
- Service name: `rag-chatbot-backend`
- Environment: Docker
- Instance type: Free

#### 3. Configure Environment Variables

In Render dashboard, add all variables from `.env`:
- `NEON_CONNECTION_STRING`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `GEMINI_API_KEY`
- etc.

**Free Tier Limits**: 750 hours/month, spins down after 15 min inactivity

---

## Better Auth Setup (Optional - For Task T085)

### 1. Choose Better Auth Deployment

Two options:
- **Self-hosted**: Deploy Better Auth on your own server
- **Better Auth Cloud**: Use managed service (if available)

### 2. Configure OAuth Providers

In Better Auth dashboard:
- Add Google OAuth (Client ID + Secret)
- Add GitHub OAuth (Client ID + Secret)
- Configure redirect URLs

### 3. Get API Credentials

- Copy Better Auth instance URL
- Generate API key for backend integration

### 4. Add to .env

```bash
BETTER_AUTH_URL=https://your-auth-instance.com
BETTER_AUTH_API_KEY=your_auth_api_key_here
```

---

## Verification Checklist

After completing all setup tasks:

- [ ] Neon Postgres connection string added to `.env`
- [ ] Qdrant collections created (`textbook_chunks_en`, `textbook_chunks_ur`)
- [ ] Qdrant URL and API key added to `.env`
- [ ] Gemini API key obtained and added to `.env`
- [ ] Railway or Render account created
- [ ] All environment variables validated

Test all connections:

```bash
cd rag-chatbot-backend
source .venv/bin/activate
python scripts/test_connections.py  # TODO: Create this script
```

---

## Cost Estimate (Monthly)

| Service | Plan | Cost |
|---------|------|------|
| Neon Postgres | Free tier | $0 |
| Qdrant Cloud | Free tier | $0 |
| Google Gemini API | Free tier | $0 |
| Railway | Free tier | $0 |
| **Total** | | **$0/month** |

All services operate within free tier limits for hackathon demo.

---

## Next Steps

After infrastructure is set up:

1. Run database migrations (Phase 2: T014-T018)
2. Test health check endpoint (Phase 2: T024)
3. Run content ingestion pipeline (Phase 2: T028-T032)

See `specs/003-rag-chatbot/tasks.md` for detailed implementation tasks.
