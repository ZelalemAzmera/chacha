import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from core.ocr import extract_text_from_image
from core.rag import retrieve_context
from core.router import route_course_to_model
from core.llm import generate_answer
from db.supabase import get_supabase_client

router = APIRouter(prefix="/ask", tags=["Ask"])
supabase = get_supabase_client()

@router.post("/")
async def ask_question(
    agent_id: str = Form(...),
    image: UploadFile = File(None),
    text_question: Optional[str] = Form(None)
):
    """
    Endpoint for asking a question. Supports an image upload or direct text.
    1. Extracts text from image if provided.
    2. Retrieves relevant context from vector DB.
    3. Routes to the optimal LLM based on the agent's course.
    4. Generates and returns the answer.
    """
    if not image and not text_question:
        raise HTTPException(status_code=400, detail="Must provide either an image or text_question.")
        
    question_text = text_question or ""
    
    # 1. OCR on image if provided
    if image:
        ext = os.path.splitext(image.filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            raise HTTPException(status_code=400, detail=f"Unsupported image format: {ext}")
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            shutil.copyfileobj(image.file, temp_file)
            temp_path = temp_file.name
            
        try:
            # Extract text from the image, specifically prompting for the question
            extracted = extract_text_from_image(temp_path, is_question=True)
            if extracted:
                question_text = f"{extracted}\n\n{question_text}".strip()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    if not question_text:
        raise HTTPException(status_code=400, detail="Could not extract any text from the question.")

    # 2. Get Agent Details (to know subject for routing)
    agent_res = supabase.table("agents").select("*").eq("id", agent_id).execute()
    if not agent_res.data:
        raise HTTPException(status_code=404, detail="Agent not found.")
    agent = agent_res.data[0]
    
    # 3. Retrieve Context from Vector DB
    context = retrieve_context(agent_id, question_text, top_k=5)
    
    # 4. Route to optimal LLM
    model_id = route_course_to_model(agent.get("category", ""))
    
    # 5. Generate Answer
    answer = generate_answer(question_text, context, model_id)
    
    # 6. Save to questions history table
    try:
        supabase.table("questions").insert({
            "agent_id": agent_id,
            "question_text": question_text,
            "answer_text": answer,
            "model_used": model_id
        }).execute()
    except Exception as e:
        print(f"Failed to log question to DB: {e}")
        
    return {
        "question": question_text,
        "answer": answer,
        "model_used": model_id,
        "context_used": bool(context.strip())
    }
