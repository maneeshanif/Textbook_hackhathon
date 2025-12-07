-- Migration: 002_create_sessions
-- Description: Create chat_sessions table for conversation threads
-- Date: 2025-12-07

CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- NULL for anonymous
    session_token VARCHAR(64),  -- For anonymous session tracking (hashed)
    language VARCHAR(5) DEFAULT 'en' CHECK (language IN ('en', 'ur')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_token ON chat_sessions(session_token) WHERE user_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_chat_sessions_cleanup ON chat_sessions(created_at) WHERE user_id IS NULL;

-- Add comments for documentation
COMMENT ON TABLE chat_sessions IS 'Conversation threads for guest and authenticated users';
COMMENT ON COLUMN chat_sessions.user_id IS 'Foreign key to users (NULL for guest users)';
COMMENT ON COLUMN chat_sessions.session_token IS 'Hashed token for anonymous session tracking';
COMMENT ON COLUMN chat_sessions.language IS 'Interface language preference (en or ur)';
COMMENT ON COLUMN chat_sessions.last_activity IS 'Last message timestamp (updated on each query)';
