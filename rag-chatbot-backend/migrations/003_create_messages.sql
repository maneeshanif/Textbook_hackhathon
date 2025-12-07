-- Migration: 003_create_messages
-- Description: Create chat_messages table for individual messages
-- Date: 2025-12-07

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',  -- Stores citations, similarity scores, etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id, created_at DESC);

-- Add comments for documentation
COMMENT ON TABLE chat_messages IS 'Individual messages (user queries and assistant responses) within sessions';
COMMENT ON COLUMN chat_messages.session_id IS 'Foreign key to chat_sessions table';
COMMENT ON COLUMN chat_messages.role IS 'Message sender (user or assistant)';
COMMENT ON COLUMN chat_messages.content IS 'Full message text (user query or assistant response)';
COMMENT ON COLUMN chat_messages.metadata IS 'JSON field for citations, similarity scores, response time, tokens';
