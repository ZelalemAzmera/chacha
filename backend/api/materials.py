import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from core.ingestion.pdf import extract_text_from_pdf
from core.ingestion.docx import extract_text_from_docx
from core.ingestion.pptx import extract_text_from_pptx
from core.ingestion.image import extract_text_from_material_image
from core.ingestion.audio import extract_text_from_audio
from core.ingestion.video import extract_text_from_video
from core.ingestion.website import extract_text_from_website
from core.ingestion.chunker import chunk_text
from core.rag import store_document_chunks
from db.supabase import get_supabase_client

router = APIRouter(prefix="/materials", tags=["Materials"])
supabase = get_supabase_client()

class WebsiteUploadReq(BaseModel):
    agent_id: str
    url: str

def process_material_background(agent_id: str, material_id: str, text: str):
    """
    Background task to chunk text, embed it, and store in pgvector.
    Updates the material status when done.
    """
    try:
        # Update status to processing
        supabase.table("materials").update({"status": "processing"}).eq("id", material_id).execute()
        
        # Chunk text
        chunks = chunk_text(text)
        
        # Store in pgvector
        success = store_document_chunks(agent_id, material_id, chunks)
        
        if success:
            supabase.table("materials").update({
                "status": "ready",
                "chunk_count": len(chunks)
            }).eq("id", material_id).execute()
            
            # Mark agent as ready if not already
            supabase.table("agents").update({"is_ready": True}).eq("id", agent_id).execute()
        else:
            supabase.table("materials").update({
                "status": "error",
                "error_message": "Failed to store chunks in vector DB."
            }).eq("id", material_id).execute()
            
    except Exception as e:
        supabase.table("materials").update({
            "status": "error",
            "error_message": str(e)
        }).eq("id", material_id).execute()

@router.post("/upload")
async def upload_material(
    background_tasks: BackgroundTasks,
    agent_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Endpoint to upload a file material (PDF, DOCX, etc.).
    Extracts text and hands off to a background task for embedding.
    """
    # Create DB entry for material
    res = supabase.table("materials").insert({
        "agent_id": agent_id,
        "file_name": file.filename,
        "file_type": "file",
        "status": "pending"
    }).execute()
    material_id = res.data[0]["id"]
    
    # Save uploaded file to temp file to process it
    ext = os.path.splitext(file.filename)[1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name
        
    try:
        text = ""
        # Route to appropriate extractor
        if ext == '.pdf':
            text = extract_text_from_pdf(temp_path)
        elif ext in ['.doc', '.docx']:
            text = extract_text_from_docx(temp_path)
        elif ext in ['.ppt', '.pptx']:
            text = extract_text_from_pptx(temp_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
            text = extract_text_from_material_image(temp_path)
        elif ext in ['.mp3', '.wav', '.m4a', '.ogg']:
            text = extract_text_from_audio(temp_path)
        elif ext in ['.mp4', '.mov', '.avi']:
            text = extract_text_from_video(temp_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        if not text.strip():
            raise ValueError("No text could be extracted from the file.")
            
        # Send to background task to chunk and embed
        background_tasks.add_task(process_material_background, agent_id, material_id, text)
        
        return {"message": "Upload successful. Processing material.", "material_id": material_id}
        
    except Exception as e:
        supabase.table("materials").update({
            "status": "error",
            "error_message": str(e)
        }).eq("id", material_id).execute()
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/url")
async def ingest_website(
    req: WebsiteUploadReq,
    background_tasks: BackgroundTasks
):
    """
    Endpoint to ingest a website URL.
    """
    res = supabase.table("materials").insert({
        "agent_id": req.agent_id,
        "file_name": req.url,
        "file_type": "website",
        "source_url": req.url,
        "status": "pending"
    }).execute()
    material_id = res.data[0]["id"]
    
    try:
        text = extract_text_from_website(req.url)
        if not text.strip():
            raise ValueError("No text could be extracted from the URL.")
            
        background_tasks.add_task(process_material_background, req.agent_id, material_id, text)
        
        return {"message": "Website scraped. Processing material.", "material_id": material_id}
    except Exception as e:
        supabase.table("materials").update({
            "status": "error",
            "error_message": str(e)
        }).eq("id", material_id).execute()
        return {"error": str(e)}
