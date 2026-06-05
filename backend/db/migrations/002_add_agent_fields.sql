-- Add AI-generated presentation fields to agents
ALTER TABLE agents ADD COLUMN IF NOT EXISTS display_title TEXT;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS icon TEXT DEFAULT '📚';
ALTER TABLE agents ADD COLUMN IF NOT EXISTS theme TEXT DEFAULT 'other';

-- Create model performance/health tracking table
CREATE TABLE IF NOT EXISTS model_health (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_id TEXT NOT NULL,
  course_type TEXT,
  response_time_ms INT,
  success BOOLEAN DEFAULT TRUE,
  checked_at TIMESTAMPTZ DEFAULT NOW()
);
