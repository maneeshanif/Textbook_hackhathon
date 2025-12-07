# ADR 0010: JWT-Based Authentication with Guest User Flow

**Date**: 2025-12-07  
**Status**: Proposed  
**Deciders**: Engineering Team  
**Related**: Feature 004-better-auth-implementation

## Context and Problem Statement

The RAG chatbot requires user authentication to:
1. Track user interactions and provide personalized experiences
2. Store persistent chat history across devices
3. Prevent abuse and implement usage limits
4. Enable future features (saved preferences, learning progress)

We need an authentication system that:
- Allows guest users to try the product (10 free interactions)
- Provides seamless transition from guest to authenticated user
- Ensures security (XSS/CSRF protection, secure token storage)
- Scales to support thousands of concurrent users
- Works across multiple devices with session management

## Decision Drivers

1. **User Experience First**: Minimize friction for first-time visitors
2. **Security**: Protect against common web vulnerabilities (OWASP Top 10)
3. **Scalability**: Handle 10,000+ concurrent users
4. **Developer Productivity**: Well-documented libraries, minimal custom code
5. **Cost**: Leverage existing infrastructure (Neon DB, Railway/Render)
6. **Framework Compatibility**: Works with FastAPI (backend) and React (frontend)

## Considered Options

### Option 1: Session-Based Authentication (Cookies Only)
Store session ID in httpOnly cookie, manage session state in Redis/DB.

**Pros**:
- Simpler implementation (no JWT complexity)
- Sessions easy to revoke (delete from DB)
- No token expiry management needed

**Cons**:
- Requires stateful backend (Redis/DB lookup on every request)
- Harder to scale horizontally (session affinity or shared Redis)
- Not ideal for mobile apps or third-party API consumers
- CSRF protection still required

### Option 2: JWT-Based Authentication (Current Proposal)
Dual-token system: short-lived access tokens (memory) + long-lived refresh tokens (httpOnly cookies).

**Pros**:
- Stateless authentication (no DB lookup per request)
- Scales horizontally (any server can verify JWT)
- Industry standard (RFC 7519), well-documented
- Works for web, mobile, and API clients
- Access tokens in memory = XSS protection

**Cons**:
- More complex implementation (token refresh logic)
- Tokens can't be revoked until expiry (mitigation: short-lived access tokens)
- Requires careful configuration (signing keys, expiry times)

### Option 3: Third-Party Auth (Auth0, Firebase, Clerk)
Outsource authentication to managed service.

**Pros**:
- No auth code to maintain
- Built-in features (MFA, social login, compliance)
- Enterprise-grade security

**Cons**:
- **Cost**: $25-100/month for 1000+ users
- **Vendor lock-in**: Hard to migrate away
- **Less control**: Can't customize auth flow (guest limit, etc.)
- **Latency**: Extra network hop for token verification

### Option 4: Better Auth + PyJWT Hybrid (Selected)
Use Better Auth TypeScript library for frontend, PyJWT for backend JWT handling.

**Pros**:
- Best of both worlds: Better Auth's DX + full backend control
- Open-source, no vendor lock-in
- Better Auth handles client-side token refresh automatically
- PyJWT is battle-tested, actively maintained
- Full customization (guest flow, token rotation, etc.)

**Cons**:
- Requires manual integration between frontend and backend
- Need to implement token refresh logic ourselves
- Better Auth is newer (less mature than Passport.js, etc.)

## Decision Outcome

**Chosen Option**: Option 4 - Better Auth + PyJWT Hybrid

We will implement JWT-based authentication with:
- **Frontend**: Better Auth (TypeScript) for token management, form handling
- **Backend**: PyJWT (Python) for token encoding/decoding, verification
- **Access Tokens**: 15-minute expiry, stored in React Context (memory only)
- **Refresh Tokens**: 7-day expiry (30 days with "Remember Me"), stored in httpOnly cookies
- **Guest Flow**: 10 free interactions tracked in sessionStorage, no backend state

### Rationale

1. **Security**: Meets OWASP standards
   - Access tokens in memory (no localStorage XSS risk)
   - Refresh tokens in httpOnly cookies (no JavaScript access)
   - SameSite=Strict cookies (CSRF protection)
   - Token rotation on refresh (prevents replay attacks)

2. **User Experience**: Frictionless onboarding
   - Guests can try chatbot immediately (no signup wall)
   - Seamless transition to authenticated user at 10-question limit
   - Auto-refresh keeps users logged in (no manual re-login)

3. **Scalability**: Stateless architecture
   - Access tokens verified without DB lookup (CPU-bound, scales horizontally)
   - Only refresh token validation requires DB hit (infrequent: every 15 min)
   - Can handle 10,000+ concurrent users on single server

4. **Developer Experience**: Best-in-class libraries
   - Better Auth has excellent TypeScript support, auto-refresh, error handling
   - PyJWT is the de-facto standard for Python (18M+ downloads/month)
   - Both libraries have comprehensive documentation and active communities

5. **Cost**: $0 marginal cost
   - No third-party auth service fees
   - Uses existing Neon DB (already provisioned)
   - Minimal compute overhead (JWT verification is fast)

## Architecture

### Token Flow Diagram

```
┌─────────────┐                                    ┌─────────────┐
│   Browser   │                                    │   Backend   │
│  (React)    │                                    │  (FastAPI)  │
└─────────────┘                                    └─────────────┘
       │                                                  │
       │ 1. POST /auth/login {email, password}           │
       ├─────────────────────────────────────────────────>│
       │                                                  │ 2. Verify credentials
       │                                                  │    (bcrypt check)
       │                                                  │
       │ 3. Set-Cookie: refresh_token=xxx (httpOnly)     │
       │    Response: {accessToken, expiresIn}           │
       │<─────────────────────────────────────────────────┤
       │                                                  │
       │ 4. Store accessToken in React Context (memory)  │
       │                                                  │
       │ 5. Every API call: Authorization: Bearer xxx    │
       ├─────────────────────────────────────────────────>│
       │                                                  │ 6. Verify JWT signature
       │                                                  │    (no DB lookup)
       │<─────────────────────────────────────────────────┤
       │                                                  │
       │ 7. 60s before expiry: POST /auth/refresh        │
       ├─────────────────────────────────────────────────>│
       │    Cookie: refresh_token=xxx                    │
       │                                                  │ 8. Verify refresh token
       │                                                  │    (DB lookup + hash check)
       │                                                  │ 9. Rotate token (delete old,
       │                                                  │    generate new)
       │ 10. Set-Cookie: refresh_token=yyy (new)         │
       │     Response: {accessToken, expiresIn}          │
       │<─────────────────────────────────────────────────┤
       │                                                  │
```

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Refresh tokens table (for revocation)
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    token_hash VARCHAR(255) UNIQUE NOT NULL,  -- bcrypt hash of token
    device_info JSONB,  -- {userAgent, ip, location}
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Security Measures

| Threat | Mitigation |
|--------|-----------|
| **XSS** | Access tokens in memory (React Context), never localStorage |
| **CSRF** | SameSite=Strict cookies, no state-changing GET endpoints |
| **Token Replay** | Rotate refresh tokens on every use, short-lived access tokens |
| **Brute Force** | Rate limiting (5 attempts/15min), exponential backoff |
| **Session Hijacking** | Bind tokens to device fingerprint (optional), log IP/location changes |
| **Password Leaks** | bcrypt with 12 rounds, enforce strong passwords (8+ chars, uppercase, number) |

## Consequences

### Positive

- **Fast authentication**: No DB lookup per request (access tokens verified in memory)
- **High availability**: Stateless = no single point of failure (Redis, etc.)
- **Future-proof**: JWT standard works for mobile apps, third-party integrations
- **User-friendly**: Auto-refresh = users stay logged in seamlessly
- **Developer-friendly**: Better Auth handles complex client-side logic (refresh, error handling)

### Negative

- **Complexity**: Token refresh logic requires careful implementation (race conditions, error handling)
- **Token revocation**: Can't instantly revoke access tokens (must wait for expiry or implement blacklist)
- **Storage overhead**: Refresh tokens stored in DB (1 row per session per user)
- **Debugging**: JWT errors can be cryptic (expired signature, invalid issuer, etc.)

### Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| **Refresh token stolen** | Short expiry (7 days), rotate on use, device fingerprinting |
| **Race condition during refresh** | Mutex lock on refresh endpoint, idempotency key |
| **Clock skew issues** | Use leeway (±60s) in JWT verification, NTP sync on servers |
| **Secret key compromise** | Rotate secret keys quarterly, monitor for suspicious activity |

## Implementation Plan

See `/specs/004-better-auth/tasks.md` for detailed implementation tasks.

**Phases**:
1. Backend JWT infrastructure (Day 1)
2. Backend auth routes & middleware (Day 1-2)
3. Frontend auth context & UI (Day 2-3)
4. Guest user flow (Day 3-4)
5. Integration & security (Day 4-5)
6. Testing & polish (Day 5-6)

**Estimated Effort**: 5-6 days (1 developer)

## Validation

### Success Criteria

- [ ] Guest users can use chatbot for 10 interactions without auth
- [ ] Auth flow completes in < 2 seconds (p95)
- [ ] Access tokens auto-refresh without user noticing
- [ ] Zero tokens stored in localStorage (security audit)
- [ ] Login endpoint rate-limited (5 attempts/15min)
- [ ] Password hashing uses bcrypt with 12+ rounds
- [ ] All auth tests passing (unit + integration + E2E)

### Metrics to Monitor

- Authentication latency (p50, p95, p99)
- Token refresh success rate
- Failed login attempts (detect brute force)
- Active sessions per user (detect account sharing)
- Token rotation errors (race conditions)

## Alternatives Considered

### Alternative 1: Magic Link Authentication (Passwordless)
Send one-time login links via email instead of passwords.

**Why Not Chosen**:
- Requires email service (SendGrid, Resend) = extra dependency + cost
- Higher friction (user must check email)
- Email deliverability issues (spam folders)
- Still need JWT/session management

### Alternative 2: OAuth-Only (Google, GitHub)
Only social login, no email/password.

**Why Not Chosen**:
- Forces users to have Google/GitHub account (excludes some users)
- Privacy concerns (tracking by OAuth providers)
- Can't customize auth flow (guest limit, etc.)
- Still need JWT/session management on our side

## References

- [RFC 7519: JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Better Auth Documentation](https://better-auth.com/docs)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [JWT Security Best Practices](https://curity.io/resources/learn/jwt-best-practices/)

## Approval

- [ ] Engineering Lead: _______________
- [ ] Security Review: _______________
- [ ] Product Owner: _______________

**Date Approved**: _____________

---

*This ADR supersedes any previous authentication decisions and is considered the authoritative source for auth architecture until amended.*
