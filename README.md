# Chacha - Ethiopian Student AI Tutor

Chacha is a personalized, course-specific AI tutor designed for Ethiopian students. It ingests course materials (PDFs, DOCX, PPTs, audio, video, web pages) and provides exact, hallucination-free answers using a free-tier stacked RAG architecture.

## Architecture

- **Frontend**: Next.js 14 App Router, React, Vanilla CSS (Glassmorphism, Dark Mode)
- **Backend**: FastAPI, Python
- **Database**: Supabase PostgreSQL with `pgvector`
- **OCR/Transcription**: Groq Llama 3.2 Vision / Whisper Large v3 (Free tier)
- **Embeddings**: Local `sentence-transformers` (Free & Fast)
- **LLM Routing**: 
  - Math/Science/Languages → Gemini 2.5 Flash
  - CS/History/Other → Groq Llama 3.3 70B

## Running Locally

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the `backend` directory with your API keys:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd website
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:3000` in your browser.

## Database Migrations

You must run the SQL script located at `backend/db/migrations/001_init.sql` in your Supabase SQL Editor to create the necessary tables (`profiles`, `agents`, `materials`, `chunks`, `questions`) and the `match_chunks` RPC function for vector similarity search.
