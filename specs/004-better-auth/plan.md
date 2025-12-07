# Implementation Plan: Better Auth with JWT & Guest Flow

**Feature**: 004-better-auth-implementation  
**Created**: 2025-12-07  
**Timeline**: 5-6 days  
**Complexity**: High (security-critical)

## Executive Summary

Implement production-ready authentication system supporting:
- Guest users (10 free interactions)
- JWT dual-token architecture (access + refresh)
- Shadcn UI components
- Security best practices (OWASP compliance)

## Technical Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: Neon Postgres
- **Libraries**:
  - PyJWT 2.8+ (JWT handling)
  - passlib[bcrypt] (password hashing)
  - python-jose (optional, JWT utilities)
  - slowapi (rate limiting)

### Frontend
- **Language**: TypeScript
- **Framework**: React 18
- **Libraries**:
  - better-auth 1.3+ (auth client)
  - react-hook-form + zod (form validation)
  - shadcn/ui (UI components)
  - axios (HTTP client)

## Architecture Decisions

See [ADR 0010](/history/adr/0010-jwt-authentication-with-guest-flow.md) for detailed rationale.

**Key Decisions**:
1. **JWT over Sessions**: Stateless, horizontally scalable
2. **Dual Tokens**: Access (15min, memory) + Refresh (7days, httpOnly cookie)
3. **Guest Flow**: 10 free interactions tracked in sessionStorage
4. **Better Auth**: Client-side token management (auto-refresh, error handling)
5. **PyJWT**: Backend token encoding/decoding (industry standard)

## Security Architecture

### Threat Mitigation Matrix

| Threat | Mitigation Strategy |
|--------|-------------------|
| **XSS** | Access tokens in React Context (never localStorage) |
| **CSRF** | SameSite=Strict cookies, no state-changing GETs |
| **Token Replay** | Rotate refresh tokens on every use |
| **Brute Force** | Rate limit: 5 login attempts per 15 minutes |
| **Session Hijacking** | Device fingerprinting (optional), IP logging |
| **Password Leaks** | bcrypt with 12 rounds, strength validation |
| **SQL Injection** | Parameterized queries (asyncpg) |

### Compliance

- **OWASP A01 (Broken Access Control)**: Role-based middleware
- **OWASP A02 (Cryptographic Failures)**: HTTPS enforced, bcrypt hashing
- **OWASP A03 (Injection)**: Input validation, parameterized queries
- **OWASP A07 (Auth Failures)**: Strong passwords, rate limiting, token rotation

## Database Schema Design

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt, 60 chars
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);
```

### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,  -- bcrypt hash, not plaintext
    device_info JSONB,  -- {userAgent, ip, location}
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_token_hash (token_hash),
    INDEX idx_expires_at (expires_at)
);
```

### Auth Events Table (Audit Log)
```sql
CREATE TABLE auth_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,  -- login, logout, refresh, failed_login
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at)
);
```

## API Contract

### Authentication Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | /api/auth/register | No | Create new user account |
| POST | /api/auth/login | No | Authenticate user |
| POST | /api/auth/refresh | Cookie | Generate new access token |
| POST | /api/auth/logout | Yes | Revoke refresh token |
| GET | /api/auth/me | Yes | Get current user info |

### JWT Payload Structure

**Access Token**:
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "user",
  "type": "access",
  "iat": 1702000000,
  "exp": 1702000900
}
```

**Refresh Token**:
```json
{
  "sub": "user-uuid",
  "type": "refresh",
  "jti": "token-uuid",
  "iat": 1702000000,
  "exp": 1702604800
}
```

## Frontend Architecture

### Component Hierarchy

```
App
├── AuthProvider (Context)
│   └── GuestProvider (Context)
│       └── ChatWidget
│           ├── GuestLimitBadge (shows "X/10")
│           ├── GuestLimitReachedDialog
│           │   └── AuthDialog
│           │       ├── Tabs (Sign Up / Log In)
│           │       ├── SignUpForm
│           │       │   └── PasswordStrengthIndicator
│           │       └── LoginForm
│           └── ChatMessages
```

### State Management

**AuthContext**:
- `user: User | null` (current user)
- `accessToken: string | null` (in-memory only)
- `isLoading: boolean`
- `error: string | null`
- `login(email, password, rememberMe)`
- `register(email, password, fullName)`
- `logout()`
- `refreshToken()`

**GuestContext**:
- `interactionCount: number` (0-10)
- `isLimitReached: boolean`
- `incrementCount()`
- `resetCount()`

## Implementation Phases

### Phase 1: Backend JWT Infrastructure (Day 1, 3-4 hours)
**Deliverable**: Working JWT service + database migrations

- [ ] Create SQL migrations (users, refresh_tokens, auth_events)
- [ ] Implement JWT service (create/verify tokens)
- [ ] Implement password service (hash/verify with bcrypt)
- [ ] Create Pydantic models (request/response)
- [ ] Unit tests for JWT service

**Acceptance**: Can generate and verify JWT tokens programmatically

### Phase 2: Backend Auth Routes (Day 1-2, 4-5 hours)
**Deliverable**: Fully functional auth API endpoints

- [ ] Implement user repository (CRUD operations)
- [ ] Implement refresh token repository (create/delete/cleanup)
- [ ] Create auth routes (/register, /login, /refresh, /logout, /me)
- [ ] Add auth middleware (JWT verification)
- [ ] Add rate limiting (5 attempts/15min)
- [ ] Integration tests for all endpoints

**Acceptance**: Can register, login, refresh, logout via Postman/curl

### Phase 3: Frontend Auth Context & UI (Day 2-3, 5-6 hours)
**Deliverable**: Working auth forms with validation

- [ ] Install dependencies (better-auth, react-hook-form, zod, shadcn)
- [ ] Create AuthContext with login/register/logout functions
- [ ] Create AuthDialog with Tabs (Sign Up / Log In)
- [ ] Create SignUpForm with validation (email, password strength)
- [ ] Create LoginForm with validation
- [ ] Add axios interceptors (attach token, handle 401)
- [ ] Component tests (forms, validation)

**Acceptance**: Can sign up and login from UI, tokens stored correctly

### Phase 4: Guest User Flow (Day 3-4, 4-5 hours)
**Deliverable**: Guest users can try 10 questions before auth

- [ ] Create GuestContext (track count in sessionStorage)
- [ ] Create GuestLimitBadge ("X/10 questions")
- [ ] Create GuestLimitReachedDialog (auto-opens at limit)
- [ ] Integrate with ChatWidget (increment count on message)
- [ ] Add guest history migration (optional)
- [ ] E2E test: Guest → 10 messages → Auth → Continue

**Acceptance**: Guest flow works end-to-end as specified

### Phase 5: Security Hardening (Day 4-5, 3-4 hours)
**Deliverable**: Production-ready security configuration

- [ ] Configure CORS (whitelist frontend domain)
- [ ] Add security headers (X-Frame-Options, CSP, etc.)
- [ ] Implement token rotation in /refresh endpoint
- [ ] Add httpOnly cookie configuration (Secure, SameSite)
- [ ] Add auth event logging (audit trail)
- [ ] Security audit (npm audit, Snyk, manual review)

**Acceptance**: Passes security checklist (see below)

### Phase 6: Testing & Polish (Day 5-6, 4-5 hours)
**Deliverable**: 100% tests passing, production-ready

- [ ] Backend: JWT service tests, auth API tests
- [ ] Frontend: Context tests, form tests, integration tests
- [ ] E2E: Full auth flow, guest flow, token refresh
- [ ] Add loading states, error toasts (UX polish)
- [ ] Update README with auth setup instructions
- [ ] Code review + final fixes

**Acceptance**: All tests passing, documented, ready to merge

## Testing Strategy

### Unit Tests (Backend)

```python
# tests/services/test_jwt_service.py
def test_create_access_token():
    token = jwt_service.create_access_token(user_id="123", email="test@example.com", role="user")
    payload = jwt_service.verify_access_token(token)
    assert payload["sub"] == "123"
    assert payload["email"] == "test@example.com"

def test_verify_expired_token():
    # Create token with past expiry
    with pytest.raises(ExpiredTokenError):
        jwt_service.verify_access_token(expired_token)

def test_password_hashing():
    password = "SecurePass123"
    hashed = password_service.hash_password(password)
    assert password_service.verify_password(password, hashed) is True
    assert password_service.verify_password("WrongPass", hashed) is False
```

### Integration Tests (Backend)

```python
# tests/api/test_auth.py
def test_register_creates_user(client):
    response = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePass123",
        "fullName": "New User"
    })
    assert response.status_code == 201
    assert "accessToken" in response.json()
    assert "user" in response.json()

def test_login_with_invalid_credentials(client):
    response = client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "WrongPassword"
    })
    assert response.status_code == 401
```

### Component Tests (Frontend)

```tsx
// src/contexts/__tests__/AuthContext.test.tsx
it('should login successfully', async () => {
  const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });
  
  await act(async () => {
    await result.current.login('user@example.com', 'password');
  });
  
  expect(result.current.user).not.toBeNull();
  expect(result.current.accessToken).toBeTruthy();
});
```

### E2E Tests (Playwright)

```typescript
// tests/e2e/guest-flow.spec.ts
test('guest user flow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Send 10 messages as guest
  for (let i = 0; i < 10; i++) {
    await page.fill('[data-testid="chat-input"]', `Question ${i + 1}`);
    await page.click('[data-testid="send-button"]');
    await page.waitForSelector('[data-testid="bot-response"]');
  }
  
  // Auth dialog should appear
  await expect(page.locator('[data-testid="auth-dialog"]')).toBeVisible();
  
  // Sign up
  await page.fill('[data-testid="email-input"]', 'test@example.com');
  await page.fill('[data-testid="password-input"]', 'SecurePass123');
  await page.fill('[data-testid="confirm-password-input"]', 'SecurePass123');
  await page.click('[data-testid="signup-button"]');
  
  // Should be able to send more messages
  await page.fill('[data-testid="chat-input"]', 'Question 11');
  await page.click('[data-testid="send-button"]');
  await page.waitForSelector('[data-testid="bot-response"]');
});
```

## Security Checklist

Before deploying to production:

- [ ] JWT_SECRET_KEY is 256+ bits (32+ characters) and randomly generated
- [ ] Access tokens stored in React Context/state (NOT localStorage)
- [ ] Refresh tokens stored in httpOnly cookies only
- [ ] HTTPS enforced in production (no HTTP)
- [ ] CORS configured with specific origin (no wildcard)
- [ ] Rate limiting enabled on /login and /register
- [ ] Passwords hashed with bcrypt (12+ rounds)
- [ ] Password strength enforced (8+ chars, uppercase, number)
- [ ] Input validation on both frontend and backend
- [ ] SQL injection prevented (parameterized queries)
- [ ] Security headers configured (X-Frame-Options, CSP, HSTS)
- [ ] Token rotation implemented (refresh tokens rotate on use)
- [ ] Auth events logged (audit trail)
- [ ] Error messages don't leak sensitive info
- [ ] npm audit / Snyk scan passed (no high/critical vulnerabilities)

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Login latency | < 300ms (p95) | Backend response time |
| Token generation | < 50ms | JWT encode time |
| Token verification | < 10ms | JWT decode time (no DB lookup) |
| Concurrent users | 10,000+ | Load testing (Locust) |
| Token refresh | < 200ms (p95) | Includes DB lookup |

## Rollout Plan

### Development
- Implement on feature branch: `004-better-auth-implementation`
- Test locally (backend + frontend)
- Code review (2 approvers required)

### Staging
- Deploy to staging environment
- Run full test suite (unit + integration + E2E)
- Security audit (manual + automated)
- User acceptance testing (UAT)

### Production
- Merge to main branch
- Deploy backend first (backward compatible)
- Deploy frontend (enable auth UI)
- Monitor error rates, latency, login success rate
- Rollback plan: Disable auth UI, allow all requests (emergency)

## Monitoring & Alerts

### Metrics to Track
- Login success rate (target: >95%)
- Token refresh success rate (target: >99%)
- Failed login attempts (alert if >100/hour)
- Token generation latency (alert if p95 >500ms)
- Active sessions per user (alert if >5, potential account sharing)

### Logs to Capture
- All auth events (login, logout, refresh, failed attempts)
- IP address, user agent, timestamp
- Error stack traces (sanitized, no sensitive data)

## Success Criteria

- [ ] Guest users can use chatbot for 10 interactions without auth
- [ ] Auth dialog auto-opens at 11th interaction
- [ ] Sign up flow completes in < 2 seconds
- [ ] Login flow completes in < 2 seconds
- [ ] Access tokens auto-refresh without user noticing
- [ ] Logout clears all tokens (client + server)
- [ ] Chat history preserved during guest → auth transition
- [ ] Zero security vulnerabilities (high/critical)
- [ ] Zero tokens found in localStorage
- [ ] All tests passing (100% for critical paths)
- [ ] Documentation complete (README, API docs, ADR)

## Future Enhancements (Post-MVP)

### P2 (Next Sprint)
- Email verification flow
- Password reset ("Forgot Password")
- Guest history migration to backend (currently UI-only)

### P3 (Future)
- Social login (Google, GitHub)
- Session management UI (view/revoke active sessions)
- Account deletion (GDPR compliance)

### P4 (Long-term)
- Multi-factor authentication (TOTP, SMS)
- Passwordless login (magic links)
- Device fingerprinting (enhanced security)
- Audit log viewer (admin panel)

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| JWT secret leaked | Critical | Low | Rotate quarterly, monitor for suspicious activity |
| Token refresh race condition | High | Medium | Mutex lock, idempotency key |
| Brute force attack | Medium | High | Rate limiting, CAPTCHA after 3 failures |
| Session fixation | High | Low | Regenerate session ID on login |
| Clock skew between servers | Medium | Low | Use NTP sync, JWT leeway (±60s) |

## References

- [Feature Specification](/specs/004-better-auth/spec.md)
- [Implementation Tasks](/specs/004-better-auth/tasks.md)
- [Quick Start Guide](/specs/004-better-auth/quickstart.md)
- [ADR 0010: Authentication Architecture](/history/adr/0010-jwt-authentication-with-guest-flow.md)
- [Better Auth Documentation](https://better-auth.com)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Status**: Ready for implementation  
**Approved By**: _______________  
**Date**: 2025-12-07
