-- Users (managed by Supabase Auth, but we can extend profiles here)
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  avatar_url TEXT,
  preferred_language TEXT DEFAULT 'am',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Course Agents
CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  subject_category TEXT,
  description TEXT,
  assigned_model TEXT,
  material_count INT DEFAULT 0,
  is_ready BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Uploaded Materials
CREATE TABLE materials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  file_name TEXT,
  file_url TEXT,
  file_type TEXT,
  source_url TEXT,
  status TEXT DEFAULT 'pending',
  chunk_count INT DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Vector Chunks (RAG knowledge base)
CREATE TABLE chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  material_id UUID REFERENCES materials(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  embedding VECTOR(384),
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Q&A Log
CREATE TABLE questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  question_image_url TEXT,
  question_text TEXT,
  answer_text TEXT,
  model_used TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector Similarity Search RPC Function
CREATE OR REPLACE FUNCTION match_chunks (
  query_embedding VECTOR(384),
  match_threshold FLOAT,
  match_count INT,
  p_agent_id UUID
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    chunks.id,
    chunks.content,
    1 - (chunks.embedding <=> query_embedding) AS similarity
  FROM chunks
  WHERE chunks.agent_id = p_agent_id
    AND 1 - (chunks.embedding <=> query_embedding) > match_threshold
  ORDER BY chunks.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
