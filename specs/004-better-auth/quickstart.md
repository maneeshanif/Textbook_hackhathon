# Better Auth Implementation - Quick Start

## Overview

This feature implements a complete JWT-based authentication system with:
- **Guest User Flow**: 10 free chatbot interactions before requiring signup
- **Dual-Token System**: Short-lived access tokens + long-lived refresh tokens
- **Shadcn UI**: Beautiful authentication dialogs
- **Security First**: XSS/CSRF protection, bcrypt hashing, rate limiting

## Prerequisites

- Neon Postgres database (running)
- Backend: Python 3.11+, FastAPI
- Frontend: Node.js 18+, React, TypeScript
- Gemini API key (for chatbot)

## Quick Setup

### 1. Backend Setup

```bash
cd rag-chatbot-backend

# Install dependencies
uv add pyjwt passlib[bcrypt] python-jose slowapi

# Generate JWT secret (save to .env)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
echo "JWT_SECRET_KEY=<generated-secret>" >> .env
echo "JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15" >> .env
echo "JWT_REFRESH_TOKEN_EXPIRE_DAYS=7" >> .env
echo "JWT_ALGORITHM=HS256" >> .env

# Run migrations
python scripts/run_migrations.py

# Start server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd book

# Install dependencies
npm install better-auth @hookform/resolvers react-hook-form zod axios js-cookie

# Install Shadcn UI components
npx shadcn@latest add dialog form input button label tabs toast

# Start dev server
npm start
```

### 3. Test Guest Flow

1. Open http://localhost:3000
2. Click chatbot widget (bottom-right)
3. Ask 10 questions as guest
4. Auth dialog should auto-open
5. Sign up with email/password
6. Verify chat unlocks

## Environment Variables

### Backend (.env)

```env
# Existing variables
NEON_CONNECTION_STRING=postgresql://...
QDRANT_URL=https://...
QDRANT_API_KEY=...
GEMINI_API_KEY=...

# New auth variables
JWT_SECRET_KEY=<256-bit-secret>  # CRITICAL: Generate with secrets.token_urlsafe(32)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ALGORITHM=HS256
```

### Frontend (.env.local)

```env
REACT_APP_API_URL=http://localhost:8000
```

## Architecture

### Token Flow

```
Guest (10 free) → Auth Dialog → Register/Login → Access Token (memory) + Refresh Token (cookie)
                                                          ↓
                                              Chatbot Unlocked (unlimited)
```

### File Structure

```
rag-chatbot-backend/
├── app/
│   ├── services/
│   │   ├── jwt_service.py          # JWT encoding/decoding
│   │   └── password_service.py     # bcrypt hashing
│   ├── api/
│   │   └── auth.py                 # /register, /login, /refresh, /logout
│   ├── middleware/
│   │   ├── auth.py                 # JWT verification
│   │   └── rate_limit.py           # Brute force protection
│   ├── models/
│   │   └── auth.py                 # Pydantic models
│   └── repositories/
│       ├── user_repository.py
│       └── refresh_token_repository.py
└── migrations/
    ├── 005_create_auth_users.sql
    ├── 006_create_refresh_tokens.sql
    └── 007_create_auth_events.sql

book/
├── src/
│   ├── contexts/
│   │   ├── AuthContext.tsx         # Auth state management
│   │   └── GuestContext.tsx        # Guest counter logic
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── AuthDialog.tsx      # Main auth modal
│   │   │   ├── SignUpForm.tsx      # Registration form
│   │   │   ├── LoginForm.tsx       # Login form
│   │   │   └── PasswordStrengthIndicator.tsx
│   │   └── ChatWidget/
│   │       ├── GuestLimitBadge.tsx # "X/10 questions" badge
│   │       └── GuestLimitReachedDialog.tsx
│   └── utils/
│       └── axiosConfig.ts          # Token interceptors
```

## API Endpoints

### POST /api/auth/register

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "fullName": "John Doe"
}
```

**Response**:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "fullName": "John Doe"
  },
  "accessToken": "eyJhbGc...",
  "expiresIn": 900
}
```

### POST /api/auth/login

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "rememberMe": false
}
```

**Response**: Same as register

### POST /api/auth/refresh

**Request**: (refresh token in httpOnly cookie)

**Response**:
```json
{
  "accessToken": "eyJhbGc...",
  "expiresIn": 900
}
```

### POST /api/auth/logout

**Response**: 204 No Content

### GET /api/auth/me

**Request**: Authorization: Bearer <accessToken>

**Response**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "fullName": "John Doe",
  "role": "user"
}
```

## Security Checklist

- [ ] JWT secret is 256+ bits (32+ characters)
- [ ] Access tokens stored in React Context (NOT localStorage)
- [ ] Refresh tokens in httpOnly cookies
- [ ] HTTPS enforced in production
- [ ] CORS whitelist (no wildcard)
- [ ] Rate limiting enabled (5 login attempts/15min)
- [ ] Passwords hashed with bcrypt (12 rounds)
- [ ] Input validation on frontend AND backend
- [ ] Security headers configured (X-Frame-Options, etc.)

## Testing

### Backend Tests

```bash
cd rag-chatbot-backend
pytest tests/services/test_jwt_service.py
pytest tests/api/test_auth.py
```

### Frontend Tests

```bash
cd book
npm test -- AuthContext.test.tsx
npm test -- GuestContext.test.tsx
npm test -- SignUpForm.test.tsx
```

### E2E Tests

```bash
cd book
npm run test:e2e -- guest-flow.spec.ts
```

## Troubleshooting

### "Invalid JWT signature"
- Check JWT_SECRET_KEY matches between token creation and verification
- Ensure no whitespace in secret key

### "Access token expired"
- Normal behavior (15-min expiry)
- Auto-refresh should trigger 60s before expiry
- Check axios interceptor is configured

### "Refresh token not found"
- User likely logged out or token expired (7 days)
- Redirect to login page

### Auth dialog doesn't open at 10 questions
- Check GuestContext is wrapping app
- Verify sessionStorage key: "guest_interaction_count"
- Check console for errors

## Next Steps

1. **Email Verification**: Add email confirmation flow (P2)
2. **Password Reset**: Implement "Forgot Password" (P2)
3. **Social Login**: Add Google/GitHub OAuth (P3)
4. **MFA**: Two-factor authentication (P4)
5. **Session Management UI**: Show active sessions in settings (P4)

## References

- [Feature Spec](/specs/004-better-auth/spec.md)
- [Implementation Tasks](/specs/004-better-auth/tasks.md)
- [ADR 0010](/history/adr/0010-jwt-authentication-with-guest-flow.md)
- [Better Auth Docs](https://better-auth.com)
- [PyJWT Docs](https://pyjwt.readthedocs.io/)

---

**Status**: Ready for implementation  
**Estimated Time**: 5-6 days  
**Priority**: P0 (Blocking for RAG chatbot)
