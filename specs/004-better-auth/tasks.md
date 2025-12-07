# Tasks: Better Auth with JWT & Guest Flow

**Feature**: 004-better-auth-implementation  
**Branch**: `004-better-auth-implementation`  
**Date**: 2025-12-07  
**Input**: Design documents from `/specs/004-better-auth/`

## Overview

Implementation tasks organized by phase to deliver a complete authentication system with guest user flow, JWT tokens, and Shadcn UI components.

**Organization Strategy**:
- Phase 1: Backend JWT Infrastructure
- Phase 2: Backend Auth Routes & Middleware
- Phase 3: Frontend Auth Context & UI Components
- Phase 4: Guest User Flow Implementation
- Phase 5: Integration & Security Hardening
- Phase 6: Testing & Polish

**Total Tasks**: 72 tasks across 6 phases  
**Estimated Timeline**: 5-6 days

---

## Format Convention

**Task Format**: `- [ ] [ID] [P?] Description with file path`

- **Checkbox**: `- [ ]` for incomplete, `- [x]` for complete
- **[ID]**: Sequential task number (T001, T002, etc.)
- **[P]**: Parallelizable (different files, no blocking dependencies)
- **Description**: Clear action with exact file path

---

## Phase 1: Backend JWT Infrastructure (Day 1, 3-4 hours)

**Purpose**: Core JWT service and database schema

### Database Schema

- [ ] T001 Create SQL migration for updated `users` table in `rag-chatbot-backend/migrations/005_create_auth_users.sql`
  - Add columns: id (UUID), email (VARCHAR UNIQUE), password_hash (VARCHAR), full_name (VARCHAR), role (VARCHAR DEFAULT 'user'), email_verified (BOOLEAN DEFAULT FALSE), created_at, updated_at
  - Add indexes on email, created_at

- [ ] T002 Create SQL migration for `refresh_tokens` table in `rag-chatbot-backend/migrations/006_create_refresh_tokens.sql`
  - Columns: id (UUID), user_id (FK to users), token_hash (VARCHAR UNIQUE), device_info (JSONB), expires_at (TIMESTAMP), created_at
  - Add indexes on user_id, token_hash, expires_at

- [ ] T003 [P] Create SQL migration for `auth_events` audit table in `rag-chatbot-backend/migrations/007_create_auth_events.sql`
  - Columns: id (UUID), user_id (FK nullable), event_type (VARCHAR), ip_address (INET), user_agent (TEXT), created_at
  - Add indexes on user_id, event_type, created_at

- [ ] T004 Run all auth migrations against Neon database

### JWT Service

- [ ] T005 Install Python dependencies: `cd rag-chatbot-backend && uv add pyjwt passlib[bcrypt] python-jose`

- [ ] T006 Create JWT configuration in `rag-chatbot-backend/app/config.py`
  - Add JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_DAYS
  - Add validation for secret key (must be 256+ bits)

- [ ] T007 Create JWT service in `rag-chatbot-backend/app/services/jwt_service.py`
  - Implement `create_access_token(user_id: UUID, email: str, role: str) -> str`
  - Implement `create_refresh_token(user_id: UUID) -> str`
  - Implement `verify_access_token(token: str) -> dict | None`
  - Implement `verify_refresh_token(token: str) -> dict | None`
  - Implement `decode_token_without_verification(token: str) -> dict | None` (for debugging)

- [ ] T008 [P] Create password hashing utilities in `rag-chatbot-backend/app/services/password_service.py`
  - Implement `hash_password(password: str) -> str` (bcrypt, rounds=12)
  - Implement `verify_password(plain_password: str, hashed_password: str) -> bool`

### Pydantic Models

- [ ] T009 Create auth request/response models in `rag-chatbot-backend/app/models/auth.py`
  - `UserRegisterRequest`: email, password, full_name (optional)
  - `UserLoginRequest`: email, password, remember_me (optional, default False)
  - `TokenResponse`: access_token, token_type="Bearer", expires_in
  - `UserResponse`: id, email, full_name, role, email_verified, created_at

- [ ] T010 Create database models in `rag-chatbot-backend/app/models/db_models.py`
  - `UserDB`: database representation with all fields
  - `RefreshTokenDB`: database representation
  - `AuthEventDB`: database representation

---

## Phase 2: Backend Auth Routes & Middleware (Day 1-2, 4-5 hours)

### Auth Repository Layer

- [ ] T011 Create user repository in `rag-chatbot-backend/app/repositories/user_repository.py`
  - Implement `create_user(email: str, password_hash: str, full_name: str) -> UserDB`
  - Implement `get_user_by_email(email: str) -> UserDB | None`
  - Implement `get_user_by_id(user_id: UUID) -> UserDB | None`
  - Implement `update_user(user_id: UUID, **fields) -> UserDB`

- [ ] T012 Create refresh token repository in `rag-chatbot-backend/app/repositories/refresh_token_repository.py`
  - Implement `create_refresh_token(user_id: UUID, token_hash: str, device_info: dict, expires_at: datetime) -> RefreshTokenDB`
  - Implement `get_refresh_token(token_hash: str) -> RefreshTokenDB | None`
  - Implement `delete_refresh_token(token_hash: str) -> bool`
  - Implement `delete_user_tokens(user_id: UUID) -> int` (logout from all devices)
  - Implement `delete_expired_tokens() -> int` (cleanup cron job)

- [ ] T013 [P] Create auth event repository in `rag-chatbot-backend/app/repositories/auth_event_repository.py`
  - Implement `log_event(user_id: UUID, event_type: str, ip: str, user_agent: str)`

### Auth Routes

- [ ] T014 Create auth router in `rag-chatbot-backend/app/api/auth.py`
  - Import dependencies (FastAPI, repositories, services)
  - Setup router with prefix `/api/auth`

- [ ] T015 Implement POST `/api/auth/register` endpoint in `rag-chatbot-backend/app/api/auth.py`
  - Validate email doesn't exist
  - Hash password
  - Create user in database
  - Generate access token
  - Generate refresh token, store hash in database
  - Set httpOnly cookie with refresh token
  - Return TokenResponse + UserResponse
  - Log auth event

- [ ] T016 Implement POST `/api/auth/login` endpoint in `rag-chatbot-backend/app/api/auth.py`
  - Validate user exists
  - Verify password
  - Handle remember_me flag (adjust refresh token expiry)
  - Generate access token
  - Generate refresh token, store hash in database
  - Set httpOnly cookie with refresh token
  - Return TokenResponse + UserResponse
  - Log auth event
  - Implement rate limiting (5 attempts per 15 min)

- [ ] T017 Implement POST `/api/auth/refresh` endpoint in `rag-chatbot-backend/app/api/auth.py`
  - Extract refresh token from httpOnly cookie
  - Verify refresh token
  - Check if token exists in database (not revoked)
  - Generate new access token
  - Rotate refresh token (delete old, create new)
  - Set new httpOnly cookie
  - Return TokenResponse
  - Log auth event

- [ ] T018 Implement POST `/api/auth/logout` endpoint in `rag-chatbot-backend/app/api/auth.py`
  - Extract refresh token from cookie
  - Delete refresh token from database
  - Clear httpOnly cookie
  - Return 204 No Content
  - Log auth event

- [ ] T019 Implement GET `/api/auth/me` endpoint in `rag-chatbot-backend/app/api/auth.py`
  - Protected route (requires access token)
  - Extract user from request.state (set by middleware)
  - Return UserResponse

### Auth Middleware

- [ ] T020 Create auth middleware in `rag-chatbot-backend/app/middleware/auth.py`
  - Implement `get_current_user(request: Request) -> UserDB | None`
  - Extract Bearer token from Authorization header
  - Verify access token using jwt_service
  - Fetch user from database
  - Inject user into request.state.user
  - Handle exceptions (invalid token, expired token)

- [ ] T021 Create auth dependency in `rag-chatbot-backend/app/dependencies.py`
  - Implement `require_auth(request: Request) -> UserDB`
  - Raises 401 if no user in request.state
  - Used as FastAPI dependency for protected routes

### Error Handling

- [ ] T022 [P] Create custom exceptions in `rag-chatbot-backend/app/exceptions/auth_exceptions.py`
  - `InvalidCredentialsError`
  - `EmailAlreadyExistsError`
  - `InvalidTokenError`
  - `ExpiredTokenError`
  - `RateLimitExceededError`

- [ ] T023 [P] Create exception handlers in `rag-chatbot-backend/app/middleware/exception_handlers.py`
  - Map auth exceptions to proper HTTP status codes
  - Return consistent error JSON format

---

## Phase 3: Frontend Auth Context & UI Components (Day 2-3, 5-6 hours)

### Dependencies & Configuration

- [ ] T024 Install frontend dependencies: `cd book && npm install better-auth @hookform/resolvers react-hook-form zod axios js-cookie`

- [ ] T025 Install Shadcn UI components: `npx shadcn@latest add dialog form input button label tabs toast`

- [ ] T026 Create axios instance with config in `book/src/utils/axiosConfig.ts`
  - Set baseURL to backend API
  - Add request interceptor to attach access token
  - Add response interceptor to handle 401 (trigger refresh)
  - Export configured axios instance

### Auth Context

- [ ] T027 Create AuthContext in `book/src/contexts/AuthContext.tsx`
  - Define `AuthContextType` interface (user, accessToken, login, register, logout, refreshToken, isLoading, error)
  - Create `AuthProvider` component
  - Implement state management for user, accessToken, isLoading, error
  - Export `useAuth()` hook

- [ ] T028 Implement `login()` function in `book/src/contexts/AuthContext.tsx`
  - Call POST `/api/auth/login` with email, password, rememberMe
  - Store accessToken in state (not localStorage)
  - Store user in state
  - Return success/error

- [ ] T029 Implement `register()` function in `book/src/contexts/AuthContext.tsx`
  - Call POST `/api/auth/register` with email, password, fullName
  - Store accessToken in state
  - Store user in state
  - Return success/error

- [ ] T030 Implement `logout()` function in `book/src/contexts/AuthContext.tsx`
  - Call POST `/api/auth/logout`
  - Clear accessToken state
  - Clear user state
  - Redirect to home page

- [ ] T031 Implement `refreshToken()` function in `book/src/contexts/AuthContext.tsx`
  - Call POST `/api/auth/refresh`
  - Update accessToken in state
  - Handle errors (redirect to login if refresh fails)

- [ ] T032 Implement auto-refresh logic in `book/src/contexts/AuthContext.tsx`
  - Use useEffect + setInterval to check token expiry
  - Trigger refresh 60 seconds before expiration
  - Decode JWT to get exp timestamp (use jwt-decode library)

- [ ] T033 Wrap app with AuthProvider in `book/src/App.tsx` or `book/docusaurus.config.ts` custom wrapper

### Shadcn Auth Components

- [ ] T034 Create AuthDialog component in `book/src/components/Auth/AuthDialog.tsx`
  - Import Shadcn Dialog components
  - Create controlled dialog with open/onOpenChange props
  - Add Tabs for "Sign Up" and "Log In"
  - Style with Tailwind classes

- [ ] T035 Create SignUpForm component in `book/src/components/Auth/SignUpForm.tsx`
  - Use React Hook Form + Zod validation
  - Define schema: email (email format), password (8+ chars, uppercase, number), confirmPassword
  - Add Form fields: email Input, password Input, confirmPassword Input
  - Add "Create Account" Button
  - Call useAuth().register() on submit
  - Show loading state during submission
  - Show error toast on failure

- [ ] T036 Create LoginForm component in `book/src/components/Auth/LoginForm.tsx`
  - Use React Hook Form + Zod validation
  - Define schema: email (email format), password (required)
  - Add Form fields: email Input, password Input
  - Add "Remember Me" checkbox
  - Add "Forgot Password?" link (disabled for MVP)
  - Add "Log In" Button
  - Call useAuth().login() on submit
  - Show loading state during submission
  - Show error toast on failure

- [ ] T037 Create PasswordStrengthIndicator component in `book/src/components/Auth/PasswordStrengthIndicator.tsx`
  - Calculate strength (weak, medium, strong) based on length, uppercase, numbers, special chars
  - Display colored progress bar (red, yellow, green)
  - Show requirements checklist below input

- [ ] T038 Integrate PasswordStrengthIndicator into SignUpForm in `book/src/components/Auth/SignUpForm.tsx`

### Protected Route Component

- [ ] T039 Create ProtectedRoute component in `book/src/components/Auth/ProtectedRoute.tsx`
  - Check if user is authenticated (useAuth().user !== null)
  - If not authenticated, show AuthDialog
  - If authenticated, render children

---

## Phase 4: Guest User Flow Implementation (Day 3-4, 4-5 hours)

### Guest Counter Logic

- [ ] T040 Create GuestContext in `book/src/contexts/GuestContext.tsx`
  - Define `GuestContextType` interface (interactionCount, incrementCount, resetCount, isLimitReached)
  - Implement state management with useState
  - Persist count to sessionStorage (key: "guest_interaction_count")
  - Load count from sessionStorage on mount
  - Export `useGuest()` hook

- [ ] T041 Add guest limit constant in `book/src/constants/auth.ts`
  - `export const GUEST_INTERACTION_LIMIT = 10`

- [ ] T042 Implement `incrementCount()` in `book/src/contexts/GuestContext.tsx`
  - Increment state
  - Save to sessionStorage
  - If count >= GUEST_INTERACTION_LIMIT, trigger auth dialog

- [ ] T043 Implement `resetCount()` in `book/src/contexts/GuestContext.tsx`
  - Called after successful authentication
  - Clear sessionStorage
  - Reset state to 0

- [ ] T044 Wrap app with GuestProvider in `book/src/App.tsx`
  - Ensure GuestProvider wraps AuthProvider

### Guest UI Components

- [ ] T045 Create GuestLimitBadge component in `book/src/components/ChatWidget/GuestLimitBadge.tsx`
  - Display "X/10 questions" badge
  - Show only when user is not authenticated (useAuth().user === null)
  - Add pulsing animation when count >= 8 (warning state)
  - Position in chat widget header

- [ ] T046 Integrate GuestLimitBadge into ChatWidget header in `book/src/components/ChatWidget/ChatWidget.tsx`

- [ ] T047 Create GuestLimitReachedDialog component in `book/src/components/ChatWidget/GuestLimitReachedDialog.tsx`
  - Extend AuthDialog with custom title and description
  - Title: "Unlock Unlimited Questions"
  - Description: "You've explored 10 questions as a guest. Create an account to continue your AI learning journey!"
  - Auto-open when guest limit reached

### Chat Integration

- [ ] T048 Add guest check to chat message handler in `book/src/components/ChatWidget/useChatWidget.ts` (or similar hook)
  - Before sending message, check if user is authenticated OR guest limit not reached
  - If guest limit reached, open auth dialog instead of sending message
  - Show toast: "Please sign up to continue chatting"

- [ ] T049 Increment guest count on successful chat message in `book/src/components/ChatWidget/useChatWidget.ts`
  - Call useGuest().incrementCount() after receiving chatbot response

### History Migration (Optional MVP Feature)

- [ ] T050 Create chat history migration utility in `book/src/utils/migrateGuestHistory.ts`
  - Load guest chat history from sessionStorage
  - Format as array of messages
  - Send to backend POST `/api/chat/migrate-history` (to be created)
  - Clear guest history from sessionStorage

- [ ] T051 Call migration utility after successful authentication in `book/src/contexts/AuthContext.tsx`
  - Trigger migrateGuestHistory() inside register() and login() success handlers

---

## Phase 5: Integration & Security Hardening (Day 4-5, 3-4 hours)

### Backend Security

- [ ] T052 Implement rate limiting middleware in `rag-chatbot-backend/app/middleware/rate_limit.py`
  - Use slowapi library
  - Apply to `/auth/login`: 5 attempts per 15 minutes per IP
  - Apply to `/auth/register`: 3 attempts per hour per IP

- [ ] T053 Add CORS configuration in `rag-chatbot-backend/app/main.py`
  - Whitelist frontend domain (no wildcard)
  - Allow credentials (cookies)
  - Expose Authorization header

- [ ] T054 Add security headers middleware in `rag-chatbot-backend/app/middleware/security_headers.py`
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security: max-age=31536000; includeSubDomains

- [ ] T055 Implement httpOnly cookie settings in auth routes
  - Secure=True (HTTPS only)
  - SameSite=Strict
  - HttpOnly=True
  - Max-Age=7 days (or 30 days with remember_me)

- [ ] T056 Add token rotation logic in `/auth/refresh` endpoint
  - Delete old refresh token from database
  - Generate new refresh token
  - Update cookie

### Frontend Security

- [ ] T057 Verify tokens are NOT stored in localStorage in `book/src/contexts/AuthContext.tsx`
  - Add console warning if localStorage is used
  - Document in comments: "Access tokens stored in memory only (React state)"

- [ ] T058 Implement axios response interceptor for token refresh in `book/src/utils/axiosConfig.ts`
  - On 401 response, call refreshToken()
  - Retry original request with new access token
  - If refresh fails, redirect to login

- [ ] T059 Add input sanitization for auth forms in `book/src/components/Auth/`
  - Trim email inputs
  - Validate email format before submission
  - Prevent XSS in error messages (escape user input)

### Environment Configuration

- [ ] T060 Add auth environment variables to `.env.example`
  - JWT_SECRET_KEY (with generation instructions)
  - JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
  - JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
  - JWT_ALGORITHM=HS256

- [ ] T061 Update README with auth setup instructions
  - Document how to generate secure JWT_SECRET_KEY
  - Document auth endpoints
  - Document guest user flow

---

## Phase 6: Testing & Polish (Day 5-6, 4-5 hours)

### Backend Tests

- [ ] T062 Create JWT service tests in `rag-chatbot-backend/tests/services/test_jwt_service.py`
  - Test `create_access_token()` → Verify payload structure (user_id, email, role, exp, iat)
  - Test `verify_access_token()` with expired token → Should raise ExpiredTokenError
  - Test `verify_access_token()` with invalid signature → Should raise InvalidTokenError
  - Test `create_refresh_token()` → Verify longer expiry

- [ ] T063 Create password service tests in `rag-chatbot-backend/tests/services/test_password_service.py`
  - Test `hash_password()` → Should return different hash each time (salt)
  - Test `verify_password()` with correct password → Should return True
  - Test `verify_password()` with incorrect password → Should return False

- [ ] T064 Create auth API tests in `rag-chatbot-backend/tests/api/test_auth.py`
  - Test POST `/auth/register` → Should return 201, access token, user
  - Test POST `/register` with duplicate email → Should return 400
  - Test POST `/login` with valid credentials → Should return 200, access token
  - Test POST `/login` with invalid credentials → Should return 401
  - Test POST `/refresh` with valid refresh token → Should return 200, new access token
  - Test POST `/refresh` with invalid refresh token → Should return 401
  - Test POST `/logout` → Should return 204, revoke refresh token
  - Test GET `/me` with valid access token → Should return user data
  - Test GET `/me` without token → Should return 401

### Frontend Tests

- [ ] T065 Create AuthContext tests in `book/src/contexts/__tests__/AuthContext.test.tsx`
  - Test `login()` success → Should update user and accessToken state
  - Test `login()` failure → Should set error state
  - Test `register()` success → Should update user and accessToken state
  - Test `logout()` → Should clear user and accessToken state
  - Test `refreshToken()` → Should update accessToken state

- [ ] T066 Create GuestContext tests in `book/src/contexts/__tests__/GuestContext.test.tsx`
  - Test `incrementCount()` → Should increment count in state and sessionStorage
  - Test `incrementCount()` to limit → Should trigger limit reached callback
  - Test `resetCount()` → Should clear state and sessionStorage

- [ ] T067 Create SignUpForm tests in `book/src/components/Auth/__tests__/SignUpForm.test.tsx`
  - Test form validation → Should show errors for invalid email, weak password, non-matching passwords
  - Test successful submission → Should call register() with form data
  - Test loading state → Should disable button during submission

- [ ] T068 Create LoginForm tests in `book/src/components/Auth/__tests__/LoginForm.test.tsx`
  - Test form validation → Should show errors for empty fields
  - Test successful submission → Should call login() with credentials

### E2E Tests (Optional, if time permits)

- [ ] T069 Create E2E test for guest user flow in `book/tests/e2e/guest-flow.spec.ts`
  - Open chatbot as guest
  - Send 10 messages
  - Verify auth dialog opens
  - Sign up with new account
  - Verify chat unlocks

- [ ] T070 Create E2E test for auth flow in `book/tests/e2e/auth-flow.spec.ts`
  - Click login button
  - Enter credentials
  - Verify redirect to chat
  - Verify user dropdown shows email

### UI Polish

- [ ] T071 Add loading skeletons to auth forms in `book/src/components/Auth/`
  - Show spinner in button during submission
  - Disable inputs during loading

- [ ] T072 Add toast notifications in `book/src/components/Auth/`
  - Success toast on login: "Welcome back!"
  - Success toast on register: "Account created successfully!"
  - Error toast on failure: Show specific error message
  - Use Shadcn Toast component

---

## Acceptance Criteria Checklist

- [ ] Guest users can use chatbot for 10 interactions without auth
- [ ] Guest counter displays "X/10 questions" in chat widget
- [ ] Auth dialog auto-opens when guest limit reached
- [ ] Sign up form validates email, password strength, matching passwords
- [ ] Login form validates credentials with backend
- [ ] Access tokens stored in React state (not localStorage)
- [ ] Refresh tokens stored in httpOnly cookies
- [ ] Access tokens auto-refresh 60 seconds before expiry
- [ ] Logout clears all tokens (client + server)
- [ ] Chat history preserved during guest → auth transition (UI only)
- [ ] All auth tests passing (unit + integration)
- [ ] Rate limiting works (5 login attempts per 15 min)
- [ ] CORS configured correctly (frontend domain whitelisted)
- [ ] Security headers present in all responses
- [ ] Password hashed with bcrypt (salt rounds ≥ 12)

---

## Success Metrics

- [ ] Auth flow completes in < 2 seconds (p95)
- [ ] Zero security vulnerabilities in audit (npm audit, Snyk)
- [ ] Zero tokens found in localStorage (manual inspection)
- [ ] 100% test coverage for auth services (backend)
- [ ] 80%+ test coverage for auth components (frontend)

---

**Status**: Ready for implementation  
**Estimated Completion**: 5-6 days (Day 1-6)  
**Blockers**: None (all dependencies documented)
