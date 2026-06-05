import time
from core.router import ModelProvider
from core.llm import generate_answer

def run_model_health_check(model_id: str) -> dict:
    """
    Pings a model to check its real-time health and latency.
    """
    start_time = time.time()
    try:
        # Ask a simple, tiny query
        res = generate_answer("1+1", "1+1=2", model_id)
        latency_ms = int((time.time() - start_time) * 1000)
        
        if "Error" in res or not res.strip():
            return {"success": False, "latency": -1}
            
        return {"success": True, "latency": latency_ms}
    except Exception:
        return {"success": False, "latency": -1}

def get_best_model(course_category: str, question_class: dict) -> str:
    """
    The 'Chacha Counciler'.
    Selects the absolute best model at ask-time based on the course subject 
    and the specific question complexity/type.
    """
    q_type = question_class.get("type", "factual")
    q_complex = question_class.get("complexity", "simple")
    requires_reasoning = question_class.get("requires_reasoning", False)
    
    cat = course_category.lower() if course_category else ""
    
    # --- STEP 1: INITIAL EXPERT MATCHING ---
    preferred_models = []
    
    # Math, Science, Coding usually need high reasoning
    if any(k in cat for k in ["math", "physics", "cs", "programming", "chemistry"]):
        if requires_reasoning or q_complex == "complex":
            preferred_models = [ModelProvider.GEMINI_FLASH_2_5, ModelProvider.GROQ_LLAMA_3_3]
        else:
            # Simple math/factual can use fast Llama
            preferred_models = [ModelProvider.GROQ_LLAMA_3_3, ModelProvider.GEMINI_FLASH_2_5]
            
    # History, Languages, Literature, Social
    elif any(k in cat for k in ["history", "social", "language", "literature", "amharic"]):
        if q_type == "creative" or q_complex == "complex":
            preferred_models = [ModelProvider.GROQ_LLAMA_3_3, ModelProvider.GEMINI_FLASH_2_5]
        else:
            preferred_models = [ModelProvider.GEMINI_FLASH_2_5, ModelProvider.GROQ_LLAMA_3_3]
            
    else:
        # Default fallback logic
        if requires_reasoning:
            preferred_models = [ModelProvider.GEMINI_FLASH_2_5, ModelProvider.GROQ_LLAMA_3_3]
        else:
            preferred_models = [ModelProvider.GROQ_LLAMA_3_3, ModelProvider.GEMINI_FLASH_2_5]
            
    # --- STEP 2: REAL-TIME HEALTH CHECK ---
    # To avoid latency, we just check the primary. If it fails, fallback.
    primary = preferred_models[0]
    health = run_model_health_check(primary)
    
    # If primary is dead or extremely slow (>5000ms for a tiny ping), use fallback
    if not health["success"] or health["latency"] > 5000:
        if len(preferred_models) > 1:
            print(f"Chacha Counciler: {primary} is slow/down ({health['latency']}ms). Falling back to {preferred_models[1]}")
            return preferred_models[1]
            
    return primary
