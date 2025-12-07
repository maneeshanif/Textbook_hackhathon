-- Migration: 005_add_jwt_auth_fields
-- Description: Add JWT authentication fields to users table and create refresh_tokens table
-- Date: 2025-12-07

-- Add password hash and role to users table for JWT authentication
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator'));

-- Create index on role for efficient queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Create refresh_tokens table for JWT token rotation
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ
);

-- Indexes for refresh_tokens
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Create auth_events table for audit logging
CREATE TABLE IF NOT EXISTS auth_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'signup', 'login', 'logout', 'token_refresh', 
        'password_reset', 'email_verification', 'failed_login'
    )),
    ip_address INET,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for auth_events
CREATE INDEX IF NOT EXISTS idx_auth_events_user_id ON auth_events(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_events_type ON auth_events(event_type);
CREATE INDEX IF NOT EXISTS idx_auth_events_created_at ON auth_events(created_at DESC);

-- Add comments for documentation
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password for email/password authentication';
COMMENT ON COLUMN users.role IS 'User role: user, admin, or moderator';
COMMENT ON TABLE refresh_tokens IS 'JWT refresh tokens with rotation support';
COMMENT ON COLUMN refresh_tokens.token_hash IS 'SHA-256 hash of refresh token for secure storage';
COMMENT ON COLUMN refresh_tokens.revoked IS 'Set to true when token is invalidated during logout';
COMMENT ON TABLE auth_events IS 'Audit log of authentication events';
