# 🤖 Physical AI Textbook - Interactive Learning Platform

> A comprehensive 15-week interactive textbook for learning Physical AI, featuring an intelligent RAG chatbot with personalized learning experiences.

[![Docusaurus](https://img.shields.io/badge/Docusaurus-3.9.2-green.svg)](https://docusaurus.io/)
[![React](https://img.shields.io/badge/React-19.0-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

## 📚 Overview

An end-to-end educational platform teaching Physical AI - the intersection of robotics, artificial intelligence, and physical systems. This project combines a beautifully designed Docusaurus textbook with an intelligent RAG (Retrieval-Augmented Generation) chatbot that provides personalized, context-aware assistance.

### 🎯 Key Features

- **📖 Interactive Textbook**: 15-week curriculum covering ROS 2, SLAM, Sensor Fusion, Computer Vision, and more
- **🤖 AI-Powered Chatbot**: Real-time assistance using RAG with Gemini 2.0 Flash
- **🔐 Authentication System**: Secure user accounts with Better Auth integration
- **🎨 Personalized Learning**: Difficulty-based responses (Beginner/Intermediate/Advanced)
- **🌍 Bilingual Support**: English and Urdu translations
- **📊 Vector Search**: Qdrant-powered semantic search across textbook content
- **💬 Real-time Streaming**: SSE-based chat for instant AI responses
- **📱 Responsive Design**: Beautiful UI inspired by modern educational platforms

## 🏗️ Architecture

```
┌─────────────────┐
│  Frontend       │
│  (Docusaurus)   │
│  React 19       │
└────────┬────────┘
         │
         │ HTTP/SSE
         │
┌────────▼────────┐      ┌──────────────┐
│  Backend        │──────►  Gemini API   │
│  (FastAPI)      │      │  (LLM)        │
└────────┬────────┘      └──────────────┘
         │
         │
    ┌────┴─────┬──────────┐
    │          │          │
┌───▼──┐  ┌───▼───┐  ┌──▼────┐
│Qdrant│  │ Neon  │  │Better │
│Vector│  │ PG DB │  │ Auth  │
└──────┘  └───────┘  └───────┘
```

### Tech Stack

#### Frontend (`/book`)
- **Framework**: Docusaurus 3.9.2
- **UI Library**: React 19.0
- **Styling**: CSS Modules, Custom Theme
- **Components**: ChatWidget, AuthModal, UserMenu
- **State Management**: React Context API
- **Testing**: Jest, React Testing Library, Playwright

#### Backend (`/rag-chatbot-backend`)
- **Framework**: FastAPI (Python 3.11+)
- **AI/ML**: 
  - Google Gemini 2.0 Flash (LLM)
  - text-embedding-004 (768-dim embeddings)
- **Databases**:
  - Neon Serverless Postgres (user data, sessions)
  - Qdrant Cloud (vector search)
- **Authentication**: Better Auth with JWT-style sessions
- **Package Manager**: uv (modern Python package manager)

## 🚀 Quick Start

### Prerequisites

- **Node.js** >= 20.0
- **Python** >= 3.11
- **uv** (Python package manager)
- **PostgreSQL** (Neon account for cloud DB)
- **Qdrant** (Cloud or self-hosted)
- **Google AI Studio** API key

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/maneeshanif/Textbook_hackhathon.git
cd Textbook_hackhathon
```

#### 2. Frontend Setup

```bash
cd book

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

#### 3. Backend Setup

```bash
cd rag-chatbot-backend

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and database URLs
```

**Required Environment Variables:**

```env
# Database
NEON_CONNECTION_STRING=postgresql://user:pass@host/db

# Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key

# AI Service
GEMINI_API_KEY=your-gemini-api-key

# Better Auth
BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key

# Configuration
SIMILARITY_THRESHOLD=0.5
MAX_CHUNKS=5
```

#### 4. Database Migration

```bash
# Run migrations to create tables
uv run python scripts/run_migration.py
```

This creates 4 tables:
- `users` - User accounts
- `accounts` - OAuth providers
- `auth_sessions` - Session tokens
- `user_preferences` - Personalization settings

#### 5. Ingest Textbook Content

```bash
# Parse MDX files and create embeddings
uv run python scripts/ingest_textbook.py
```

This will:
- Parse all `.mdx` files from `/book/docs`
- Generate embeddings using Gemini
- Store vectors in Qdrant
- Create metadata for citations

#### 6. Start Backend Server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API available at `http://localhost:8000`
API Documentation at `http://localhost:8000/docs`

## 📖 Curriculum Structure

### Module 1: Foundations (Weeks 1-5)
- **Week 1-2**: Introduction to Physical AI & ROS 2
- **Week 3-5**: Core Concepts, tf2, and Sensor Integration

### Module 2: Perception (Weeks 6-10)
- **Week 6-8**: SLAM, Computer Vision, Sensor Fusion
- **Week 9-10**: Advanced Perception Techniques

### Module 3: Intelligence (Weeks 11-13)
- **Week 11-13**: ML Integration, Reinforcement Learning

### Module 4: Real-World Applications (Weeks 14-15)
- **Week 14-15**: Capstone Project & Industry Integration

## 🎓 Learning Features

### Personalized AI Assistance

The chatbot adapts responses based on user preferences:

**Beginner Level:**
- Simple explanations without jargon
- Analogies and real-world examples
- Step-by-step breakdowns

**Intermediate Level:**
- Balanced technical depth
- Code examples with explanations
- Links to related concepts

**Advanced Level:**
- Detailed technical explanations
- Mathematical formulations
- Research paper references

### Interactive Components

- **📝 Chapter Headers**: Difficulty badges, time estimates, prerequisites
- **💬 Chat Widget**: Contextual help with text selection support
- **📚 Glossary**: 60+ technical terms with cross-references
- **🔗 Citations**: Source tracking for all AI responses

## 🔌 API Endpoints

### Authentication (`/api/auth`)
- `POST /signup` - Register new user
- `POST /login` - User login
- `POST /logout` - Session termination
- `GET /me` - Current user profile
- `GET /preferences` - User preferences
- `PUT /preferences` - Update preferences

### Chat (`/api/chat`)
- `POST /query` - Submit question (SSE streaming)
- Supports:
  - Anonymous & authenticated users
  - Text selection context
  - Real-time streaming responses
  - Citation tracking

### Health (`/api`)
- `GET /health` - Service health check
- `GET /health/db` - Database connectivity
- `GET /health/qdrant` - Vector DB status
- `GET /health/gemini` - AI service status

## 🧪 Testing

### Frontend Tests

```bash
cd book

# Unit tests
npm test

# Coverage report
npm run test:coverage

# E2E tests
npm run test:e2e
```

### Backend Tests

```bash
cd rag-chatbot-backend

# Run pytest (when implemented)
pytest tests/
```

## 📊 Performance Metrics

- **Vector Search**: ~2.5s average query time
- **LLM Generation**: ~1-3s for streaming start
- **Similarity Threshold**: 0.5 (cosine similarity)
- **Max Context Chunks**: 5 per query
- **Session Token Expiry**: 30 days
- **Database Connections**: Pooled (asyncpg)

## 🔒 Security Features

- **Password Hashing**: SHA256 secure hashing
- **Session Management**: 30-day JWT-style tokens
- **CORS Protection**: Configurable allowed origins
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Content sanitization
- **Rate Limiting**: (Planned) Request throttling

## 🌐 Deployment

### Frontend (Vercel)

```bash
# Build for production
npm run build

# Deploy to Vercel
vercel --prod
```

### Backend (Railway/Render/AWS)

```bash
# Build Docker image
docker build -t rag-chatbot-backend .

# Run container
docker run -p 8000:8000 --env-file .env rag-chatbot-backend
```

## 📈 Future Enhancements

- [ ] Email verification flow
- [ ] OAuth providers (Google, GitHub)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support beyond English/Urdu
- [ ] Offline mode with service workers
- [ ] Voice input/output for accessibility
- [ ] Collaborative learning features
- [ ] Progress tracking and achievements
- [ ] Quiz generation from content
- [ ] Jupyter notebook integration

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Create ADRs for architectural decisions
- Use PHR template for prompt history

## 📝 Documentation

- **[Quickstart Guide](QUICKSTART.md)**: Get started in 5 minutes
- **[Technical Overview](rag-chatbot-backend/TECHNICAL_OVERVIEW.md)**: Architecture deep-dive
- **[Infrastructure Setup](rag-chatbot-backend/INFRASTRUCTURE_SETUP.md)**: Cloud services guide
- **[ADRs](history/adr/)**: Architectural decision records
- **[PHRs](history/prompts/)**: Prompt history records

## 🎯 Project Status

**Current Phase**: ✅ Phase 3 Complete (RAG Chatbot with Auth)

**Completed Features:**
- ✅ Docusaurus textbook with 4 modules
- ✅ RAG chatbot backend with FastAPI
- ✅ Better Auth integration
- ✅ User preferences and personalization
- ✅ Vector search with Qdrant
- ✅ Gemini 2.0 Flash integration
- ✅ Frontend React components
- ✅ Database migrations
- ✅ Glossary system

**In Progress:**
- 🚧 Urdu translations
- 🚧 Advanced testing suite
- 🚧 Performance optimizations

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Manees Hanif** - [@maneeshanif](https://github.com/maneeshanif)

## 🙏 Acknowledgments

- Google Gemini team for AI capabilities
- Qdrant for vector search infrastructure
- Neon for serverless Postgres
- Docusaurus team for documentation framework
- Better Auth for authentication system
- The Physical AI research community

## 📞 Support

For questions, issues, or suggestions:

- **GitHub Issues**: [Create an issue](https://github.com/maneeshanif/Textbook_hackhathon/issues)
- **Discussions**: [Join discussions](https://github.com/maneeshanif/Textbook_hackhathon/discussions)

---

**Built with ❤️ for the Physical AI community**

*Last Updated: December 7, 2025*
