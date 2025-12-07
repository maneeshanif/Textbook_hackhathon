-- Migration: 004_create_feedback
-- Description: Create feedback_ratings table for user feedback (thumbs up/down)
-- Date: 2025-12-07

CREATE TABLE IF NOT EXISTS feedback_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL CHECK (rating IN (1, -1)),  -- 1 = thumbs up, -1 = thumbs down
    feedback_text TEXT,  -- Optional user comment
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_ratings_message ON feedback_ratings(message_id);
CREATE INDEX IF NOT EXISTS idx_feedback_ratings_created ON feedback_ratings(created_at DESC);

-- Add comments for documentation
COMMENT ON TABLE feedback_ratings IS 'User feedback (thumbs up/down) for assistant responses';
COMMENT ON COLUMN feedback_ratings.message_id IS 'Foreign key to chat_messages (assistant messages only)';
COMMENT ON COLUMN feedback_ratings.rating IS '1 for positive (thumbs up), -1 for negative (thumbs down)';
COMMENT ON COLUMN feedback_ratings.feedback_text IS 'Optional text feedback from user';
