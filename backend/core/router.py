from enum import Enum

class ModelProvider(str, Enum):
    GROQ_LLAMA_3_3 = "groq/llama-3.3-70b-versatile"
    GROQ_LLAMA_3_2_VISION = "groq/llama-3.2-11b-vision-preview"
    GEMINI_FLASH_2_5 = "gemini/gemini-2.5-flash"

def route_course_to_model(course_category: str) -> str:
    """
    Routes a course to the optimal free-tier LLM based on subject domain.
    """
    category = course_category.lower() if course_category else ""
    
    if any(k in category for k in ["history", "geography", "social", "civics", "ethiopia"]):
        return ModelProvider.GEMINI_FLASH_2_5
    elif any(k in category for k in ["biology", "chemistry", "health", "medicine"]):
        return ModelProvider.GEMINI_FLASH_2_5
    elif any(k in category for k in ["computer", "programming", "cs", "math", "physics"]):
        return ModelProvider.GROQ_LLAMA_3_3
    elif any(k in category for k in ["language", "literature", "amharic", "english"]):
        return ModelProvider.GEMINI_FLASH_2_5
    else:
        # Default fallback
        return ModelProvider.GROQ_LLAMA_3_3
