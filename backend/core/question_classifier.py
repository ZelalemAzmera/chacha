import json
from groq import Groq
from core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def classify_question(question: str) -> dict:
    """
    Analyzes the specific question asked by the student to determine its 
    type, complexity, and optimal model requirements.
    """
    if not settings.GROQ_API_KEY:
        return {"type": "factual", "complexity": "simple", "requires_reasoning": False}
        
    prompt = f"""
    Analyze the following student question:
    "{question}"
    
    Categorize it strictly into a JSON object with:
    1. "type": "factual" | "calculation" | "reasoning" | "creative" | "coding"
    2. "complexity": "simple" | "medium" | "complex"
    3. "requires_reasoning": boolean (true if it requires multi-step logic or deep thought)
    
    Respond ONLY with valid JSON.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Fastest model for classification
            messages=[
                {"role": "system", "content": "You are a JSON generator. Do not output anything outside the JSON structure."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        
        result_text = completion.choices[0].message.content
        return json.loads(result_text)
    except Exception as e:
        print(f"Error classifying question: {e}")
        return {"type": "factual", "complexity": "simple", "requires_reasoning": False}
