-- Migration: 001_create_users
-- Description: Create users table for authenticated user accounts (Better Auth integration)
-- Date: 2025-12-07

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Add comment for documentation
COMMENT ON TABLE users IS 'Authenticated user accounts (Better Auth integration)';
COMMENT ON COLUMN users.id IS 'Unique user identifier (UUID for Better Auth compatibility)';
COMMENT ON COLUMN users.email IS 'User email address (unique constraint for authentication)';
COMMENT ON COLUMN users.email_verified IS 'Email verification status (managed by Better Auth)';
