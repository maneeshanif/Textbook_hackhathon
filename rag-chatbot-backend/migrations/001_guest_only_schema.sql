-- Migration: 001_guest_only_schema
-- Description: Simple guest-only schema for RAG chatbot (no authentication)
-- Date: 2025-12-08

-- Drop all auth-related tables
DROP TABLE IF EXISTS feedback_ratings CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chat_sessions CASCADE;
DROP TABLE IF EXISTS auth_events CASCADE;
DROP TABLE IF EXISTS refresh_tokens CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS auth_sessions CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create simple chat sessions table (guest-only)
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    language VARCHAR(5) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_token ON chat_sessions(session_token);
CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at DESC);

-- Create chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at DESC);

-- Create feedback ratings table
CREATE TABLE feedback_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating IN (-1, 1)),
    feedback_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feedback_ratings_message_id ON feedback_ratings(message_id);
CREATE INDEX idx_feedback_ratings_created_at ON feedback_ratings(created_at DESC);

-- Add comments for documentation
COMMENT ON TABLE chat_sessions IS 'Guest chat sessions (no authentication required)';
COMMENT ON TABLE chat_messages IS 'Chat message history';
COMMENT ON TABLE feedback_ratings IS 'User feedback on chat responses';
