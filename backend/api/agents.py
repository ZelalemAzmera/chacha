from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from db.supabase import get_supabase_client
from core.naming import generate_agent_identity

router = APIRouter(prefix="/agents", tags=["Agents"])
supabase = get_supabase_client()

class CreateAgentRequest(BaseModel):
    name: str
    user_id: Optional[str] = None

@router.post("/create")
async def create_agent(req: CreateAgentRequest):
    """
    Creates an agent with AI-generated title, icon, and theme based on the course name.
    """
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Course name is required.")
        
    # 1. AI Generation for identity
    identity = generate_agent_identity(req.name)
    
    # 2. Insert into DB
    try:
        agent_data = {
            "name": req.name,
            "display_title": identity.get("display_title", req.name),
            "icon": identity.get("icon", "📚"),
            "theme": identity.get("theme", "other"),
            "subject_category": identity.get("category", "other"),
        }
        
        if req.user_id:
            agent_data["user_id"] = req.user_id
            
        res = supabase.table("agents").insert(agent_data).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create agent in DB.")
            
        return res.data[0]
    except Exception as e:
        print(f"Agent creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
