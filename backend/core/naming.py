import json
from groq import Groq
from core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_agent_identity(course_name: str) -> dict:
    """
    Uses a fast LLM to generate a catchy display title, emoji icon, 
    and UI theme based on the user's raw course name.
    """
    if not settings.GROQ_API_KEY:
        return {"display_title": course_name, "icon": "📚", "theme": "other", "category": "other"}
        
    prompt = f"""
    Analyze this course name: "{course_name}"
    Generate a JSON object with:
    1. "display_title": A polished version of the name.
    2. "icon": A single relevant emoji.
    3. "theme": One of [math, science, history, cs, language, other].
    4. "category": A 1-2 word broad academic category (e.g., Mathematics, Literature, Biology).
    
    Respond ONLY with valid JSON.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a JSON generator. Do not output anything outside the JSON structure."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        
        result_text = completion.choices[0].message.content
        return json.loads(result_text)
    except Exception as e:
        print(f"Error generating agent identity: {e}")
        return {"display_title": course_name, "icon": "📚", "theme": "other", "category": "other"}
