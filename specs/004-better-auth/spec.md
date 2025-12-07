# Feature Specification: Better Auth with JWT & Guest Flow

**Feature Branch**: `004-better-auth-implementation`  
**Created**: 2025-12-07  
**Status**: Draft  
**Priority**: P0 (Blocking - Required for RAG chatbot)

## Executive Summary

Implement a comprehensive authentication system using Better Auth (TypeScript/React) and PyJWT (Python/FastAPI) that supports:
- **Guest User Flow**: Allow 10 free chatbot interactions before requiring authentication
- **JWT-based Authentication**: Dual-token system (access + refresh tokens) similar to Facebook
- **Shadcn UI Integration**: Beautiful, accessible authentication components
- **Persistent Sessions**: Seamless transition from guest to authenticated user
- **Security First**: Proper token rotation, CSRF protection, XSS prevention

## User Stories

### User Story 1: Guest User Experience (Priority: P0)

**As a** first-time visitor  
**I want to** use the chatbot without creating an account  
**So that** I can evaluate the product before committing to signup

**Acceptance Criteria**:
1. User can immediately interact with chatbot on page load (no auth required)
2. System tracks guest interactions using browser fingerprinting or sessionStorage
3. After 10 interactions, a Shadcn Dialog appears with signup/login prompt
4. Dialog displays: "You've used 10/10 free questions. Sign up to continue learning!"
5. Guest session data is preserved and migrated upon signup
6. Guest users see a persistent counter: "X/10 questions remaining"

**Technical Requirements**:
- Frontend: React Context API to manage guest state
- Backend: No database writes for guest users (stateless validation)
- Storage: sessionStorage for guest interaction count
- UI: Shadcn Dialog component with smooth transition

**Edge Cases**:
- What if user clears sessionStorage mid-session?
  - Reset counter, treat as new guest
- What if user opens multiple tabs?
  - Share counter across tabs using localStorage events
- What if user tries to bypass limit by opening incognito?
  - Accept this as expected behavior (no complex fingerprinting)

---

### User Story 2: Seamless Authentication (Priority: P0)

**As a** guest user who hit the 10-question limit  
**I want to** quickly sign up or log in  
**So that** I can continue my learning without losing context

**Acceptance Criteria**:
1. Dialog offers both "Sign Up" and "Log In" options
2. Sign Up form has: Email, Password, Confirm Password (Shadcn Input components)
3. Log In form has: Email, Password, "Forgot Password?" link
4. Form validation shows real-time errors (via React Hook Form + Zod)
5. Upon successful authentication, dialog closes and chatbot unlocks
6. Previous guest chat history is preserved in UI (optional backend migration)
7. User sees success toast: "Welcome! Your chat history has been saved."

**Technical Requirements**:
- Frontend: Shadcn Form + Input + Button + Dialog components
- Backend: FastAPI endpoints for `/auth/register`, `/auth/login`
- Validation: Zod schema on frontend, Pydantic models on backend
- Security: HTTPS only, password hashing (bcrypt), rate limiting

**Edge Cases**:
- Email already exists during signup?
  - Show error: "This email is already registered. Log in instead?"
- Invalid credentials during login?
  - Show error: "Incorrect email or password" (don't reveal which is wrong)
- Network failure during submission?
  - Show error toast: "Connection lost. Please try again."

---

### User Story 3: JWT Token Management (Priority: P0)

**As a** system architect  
**I want** a secure dual-token system (access + refresh)  
**So that** we balance security with user experience

**Acceptance Criteria**:
1. **Access Token**: Short-lived (15 minutes), stored in memory (React state)
2. **Refresh Token**: Long-lived (7 days), stored in httpOnly cookie
3. Access token auto-refreshes 60 seconds before expiration
4. Refresh token rotates on every use (prevents replay attacks)
5. Logout invalidates both tokens and clears all client storage
6. Token payload includes: userId, email, role, iat, exp

**Technical Requirements**:
- **Backend (Python/FastAPI)**:
  - PyJWT for encoding/decoding
  - Access token: HS256 algorithm, 15-min expiry
  - Refresh token: HS256 algorithm, 7-day expiry, stored in Neon DB
  - Middleware to validate access token on protected routes
- **Frontend (React/TypeScript)**:
  - Better Auth client for token management
  - Axios interceptor to attach access token to requests
  - Auto-refresh logic using setInterval or interceptor pattern
- **Security**:
  - Refresh tokens: httpOnly, secure, sameSite=strict cookies
  - Access tokens: Never stored in localStorage (XSS risk)
  - Invalidate refresh tokens on logout, password change, suspicious activity

**Token Flow**:
```
1. User logs in → Backend returns { accessToken, refreshToken }
2. Backend sets httpOnly cookie with refreshToken
3. Frontend stores accessToken in React Context (memory)
4. Every API call includes: Authorization: Bearer <accessToken>
5. 60s before expiry → Frontend calls /auth/refresh
6. Backend validates refreshToken from cookie → Returns new accessToken
7. Backend invalidates old refreshToken, stores new one in DB
```

**Edge Cases**:
- Refresh token expired or invalid?
  - Redirect to login page, clear all tokens
- User has multiple devices logged in?
  - Allow multi-device sessions (store multiple refresh tokens in DB)
- Concurrent refresh requests?
  - Use mutex/lock to prevent race conditions

---

### User Story 4: Session Persistence (Priority: P1)

**As an** authenticated user  
**I want** to stay logged in across browser sessions  
**So that** I don't have to re-enter credentials every visit

**Acceptance Criteria**:
1. User checks "Remember Me" during login → Refresh token lasts 30 days
2. Without "Remember Me" → Refresh token lasts 7 days
3. User can view active sessions in settings page
4. User can revoke individual sessions ("Log out from other devices")
5. System automatically revokes tokens older than max age

**Technical Requirements**:
- Database: `sessions` table with userId, refreshToken, deviceInfo, createdAt, expiresAt
- Backend: Cron job to purge expired tokens daily
- Frontend: Settings page listing active sessions (device, location, last active)

---

### User Story 5: Social Authentication (Priority: P2 - Bonus)

**As a** user  
**I want to** log in with Google/GitHub  
**So that** I don't have to manage another password

**Acceptance Criteria**:
1. Dialog shows "Continue with Google" and "Continue with GitHub" buttons
2. OAuth flow redirects to provider, then back to app with auth code
3. Backend exchanges auth code for tokens, creates/updates user in DB
4. User is redirected to chatbot with access token

**Technical Requirements**:
- Backend: Better Auth OAuth plugin for Google, GitHub
- Frontend: OAuth buttons in Shadcn Dialog
- Security: PKCE flow for public clients

---

## Technical Architecture

### Backend (Python/FastAPI + PyJWT)

**Dependencies**:
```toml
[tool.poetry.dependencies]
pyjwt = "^2.8.0"
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-jose = "^3.3.0"  # Optional: for better JWT utilities
```

**Key Components**:
1. **JWT Service** (`app/services/jwt_service.py`):
   - `create_access_token(user_id, email, role)` → str
   - `create_refresh_token(user_id)` → str
   - `verify_access_token(token)` → dict | None
   - `verify_refresh_token(token)` → dict | None

2. **Auth Routes** (`app/api/auth.py`):
   - `POST /auth/register` → Creates user, returns tokens
   - `POST /auth/login` → Validates credentials, returns tokens
   - `POST /auth/refresh` → Validates refresh token (from cookie), returns new access token
   - `POST /auth/logout` → Invalidates refresh token
   - `GET /auth/me` → Returns current user info (protected)

3. **Auth Middleware** (`app/middleware/auth.py`):
   - Extracts Bearer token from Authorization header
   - Validates access token
   - Injects user data into request.state

4. **Database Models** (`app/models/auth.py`):
   ```python
   class User:
       id: UUID
       email: str
       password_hash: str
       full_name: str | None
       created_at: datetime
   
   class RefreshToken:
       id: UUID
       user_id: UUID
       token_hash: str  # Store hash, not plaintext
       device_info: str | None
       expires_at: datetime
       created_at: datetime
   ```

**Environment Variables**:
```env
JWT_SECRET_KEY=<random-256-bit-secret>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ALGORITHM=HS256
```

---

### Frontend (React/TypeScript + Better Auth + Shadcn)

**Dependencies**:
```json
{
  "dependencies": {
    "better-auth": "^1.3.4",
    "@hookform/resolvers": "^3.3.4",
    "react-hook-form": "^7.49.3",
    "zod": "^3.22.4",
    "axios": "^1.6.5"
  }
}

```

**Key Components**:

1. **Auth Context** (`book/src/contexts/AuthContext.tsx`):
   ```tsx
   interface AuthContextType {
     user: User | null
     accessToken: string | null
     login: (email: string, password: string) => Promise<void>
     register: (email: string, password: string) => Promise<void>
     logout: () => Promise<void>
     refreshToken: () => Promise<void>
     guestInteractionCount: number
     incrementGuestCount: () => void
   }
   ```

2. **Auth Dialog** (`book/src/components/Auth/AuthDialog.tsx`):
   - Shadcn Dialog with tabs for "Sign Up" and "Log In"
   - Forms use React Hook Form + Zod validation
   - Auto-opens when guest limit reached

3. **Token Interceptor** (`book/src/utils/axiosConfig.ts`):
   ```ts
   // Attach access token to all requests
   axios.interceptors.request.use(config => {
     const token = getAccessToken()
     if (token) {
       config.headers.Authorization = `Bearer ${token}`
     }
     return config
   })
   
   // Auto-refresh on 401 responses
   axios.interceptors.response.use(
     response => response,
     async error => {
       if (error.response?.status === 401) {
         await refreshAccessToken()
         return axios.request(error.config)
       }
       return Promise.reject(error)
     }
   )
   ```

4. **Guest Limit Badge** (`book/src/components/ChatWidget/GuestLimitBadge.tsx`):
   - Shows "X/10 questions" badge in chat header
   - Pulses when count reaches 8 (warning state)

---

## UI/UX Design (Shadcn Components)

### Authentication Dialog

**Components Used**:
- `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`
- `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent`
- `Form`, `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormMessage`
- `Input`, `Button`, `Label`

**Visual States**:
1. **Guest Limit Reached**:
   - Dialog auto-opens with glowing border
   - Title: "Unlock Unlimited Questions"
   - Description: "You've explored 10 questions as a guest. Create an account to continue your AI learning journey!"

2. **Sign Up Tab**:
   - Email input (with validation)
   - Password input (with strength indicator)
   - Confirm Password input
   - "Create Account" button (primary)
   - "Already have an account? Log in" link

3. **Log In Tab**:
   - Email input
   - Password input
   - "Remember Me" checkbox
   - "Forgot Password?" link
   - "Log In" button (primary)
   - "Don't have an account? Sign up" link

**Validation Rules**:
```ts
const signUpSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Must contain uppercase letter")
    .regex(/[0-9]/, "Must contain number"),
  confirmPassword: z.string()
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
})
```

---

## Security Considerations

### Threat Model

| Threat | Mitigation |
|--------|-----------|
| **XSS (Cross-Site Scripting)** | Never store tokens in localStorage; use httpOnly cookies for refresh tokens |
| **CSRF (Cross-Site Request Forgery)** | SameSite=Strict cookies; CORS whitelisting |
| **Token Replay Attacks** | Rotate refresh tokens on every use; short-lived access tokens |
| **Brute Force Attacks** | Rate limiting (5 attempts per 15 min); account lockout after 10 failed attempts |
| **Session Hijacking** | Bind tokens to device fingerprint; log suspicious location changes |
| **Password Leaks** | bcrypt with salt rounds=12; enforce password strength; breach detection API |

### OWASP Compliance
- [ ] A01: Broken Access Control → Role-based middleware
- [ ] A02: Cryptographic Failures → HTTPS enforced, bcrypt for passwords
- [ ] A03: Injection → Parameterized queries (SQLAlchemy)
- [ ] A07: Identification & Authentication Failures → MFA ready (future), session management

---

## Database Schema

### New Tables

```sql
-- Users table (extends existing if present)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB,  -- {userAgent, ip, location}
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
);

-- Auth events (audit log)
CREATE TABLE auth_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,  -- login, logout, refresh, failed_login
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Contract

### POST /api/auth/register

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "fullName": "John Doe"
}
```

**Response (201)**:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "fullName": "John Doe"
  },
  "accessToken": "eyJhbGc...",
  "expiresIn": 900  // seconds
}
```
*Note: Refresh token set in httpOnly cookie*

**Errors**:
- `400`: Email already exists
- `422`: Invalid email format or weak password

---

### POST /api/auth/login

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "rememberMe": false
}
```

**Response (200)**: Same as `/register`

**Errors**:
- `401`: Invalid credentials
- `429`: Too many failed attempts (rate limited)

---

### POST /api/auth/refresh

**Request**:
```http
POST /api/auth/refresh HTTP/1.1
Cookie: refresh_token=<token>
```

**Response (200)**:
```json
{
  "accessToken": "eyJhbGc...",
  "expiresIn": 900
}
```

**Errors**:
- `401`: Invalid or expired refresh token

---

### POST /api/auth/logout

**Request**:
```http
POST /api/auth/logout HTTP/1.1
Authorization: Bearer <accessToken>
Cookie: refresh_token=<token>
```

**Response (204)**: No content

---

### GET /api/auth/me

**Request**:
```http
GET /api/auth/me HTTP/1.1
Authorization: Bearer <accessToken>
```

**Response (200)**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "fullName": "John Doe",
  "role": "user",
  "emailVerified": false
}
```

---

## Testing Strategy

### Unit Tests

**Backend (pytest)**:
- `test_create_access_token()` → Verify payload structure
- `test_verify_expired_token()` → Should raise exception
- `test_password_hashing()` → bcrypt correctness
- `test_refresh_token_rotation()` → Old token invalidated

**Frontend (Jest + React Testing Library)**:
- `test_guest_counter_increment()` → Local state updates
- `test_auth_dialog_opens_at_limit()` → Dialog visibility
- `test_form_validation_errors()` → Zod schema validation
- `test_token_stored_in_memory()` → Not in localStorage

### Integration Tests

**API Tests (pytest + httpx)**:
- `test_register_login_refresh_flow()` → Full auth cycle
- `test_protected_route_without_token()` → 401 response
- `test_concurrent_refresh_requests()` → Race condition handling

### E2E Tests (Playwright)

- `test_guest_user_workflow()` → 10 questions → Dialog → Signup → Continue chatting
- `test_remember_me_persistence()` → Close browser → Reopen → Still logged in

---

## Non-Functional Requirements

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| **Auth Response Time** | < 300ms (p95) | `/auth/login`, `/auth/refresh` latency |
| **Token Generation** | < 50ms | JWT encode time |
| **Concurrent Users** | 10,000+ | Load testing with Locust |
| **Availability** | 99.9% | Uptime monitoring (Railway/Render) |
| **GDPR Compliance** | Full | User data deletion API, consent tracking |

---

## Migration Path

### Phase 1: Backend Implementation (Days 1-2)
- [ ] Setup JWT service with PyJWT
- [ ] Create auth routes (register, login, refresh, logout)
- [ ] Add auth middleware
- [ ] Create database migrations
- [ ] Write unit tests

### Phase 2: Frontend Implementation (Days 3-4)
- [ ] Create AuthContext
- [ ] Build Shadcn auth dialog components
- [ ] Implement guest counter logic
- [ ] Add axios interceptors
- [ ] Write component tests

### Phase 3: Integration (Day 5)
- [ ] Connect frontend to backend APIs
- [ ] Test guest → authenticated flow
- [ ] Test token refresh flow
- [ ] Security audit (rate limiting, CORS, etc.)

### Phase 4: Polish (Day 6)
- [ ] Add loading states, error toasts
- [ ] Implement "Remember Me" feature
- [ ] Add session management UI
- [ ] E2E testing

---

## Success Metrics

- [ ] Guest users can ask 10 questions without auth
- [ ] Auth dialog opens automatically at limit
- [ ] Login/signup completes in < 2 seconds
- [ ] Access token auto-refreshes without user noticing
- [ ] Zero tokens stored in localStorage (security audit passes)
- [ ] Chat history preserved across guest → auth transition
- [ ] 100% of auth tests passing (unit + integration + E2E)

---

## Open Questions

1. **Email Verification**: Require email verification before chatbot access?
   - **Decision**: No for MVP (adds friction). Add as P2 feature.

2. **Password Reset Flow**: How to handle "Forgot Password"?
   - **Decision**: Send reset link via email (use SendGrid/Resend). Implement in Phase 4.

3. **Multi-Factor Authentication (MFA)**: Support TOTP/SMS?
   - **Decision**: Not for MVP. Plan for P3 (bonus points).

4. **Rate Limiting Strategy**: Where to implement (Nginx, FastAPI, or both)?
   - **Decision**: FastAPI middleware using `slowapi` library.

5. **Guest History Migration**: Store guest questions in backend or just UI?
   - **Decision**: UI only for MVP (simpler). Backend migration in P2.

---

## References

- [Better Auth Documentation](https://better-auth.com)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Shadcn UI Components](https://ui.shadcn.com)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [RFC 7519: JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)

---

**Last Updated**: 2025-12-07  
**Status**: Ready for implementation  
**Approval**: Pending review
