from groq import Groq
import google.generativeai as genai
from core.config import settings
from core.router import ModelProvider

# Initialize clients
groq_client = Groq(api_key=settings.GROQ_API_KEY)

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_answer(question: str, context: str, model_id: str) -> str:
    """
    Generates an answer using the designated model (Groq or Gemini)
    based on the retrieved context.
    """
    system_prompt = (
        "You are Chacha, an expert AI tutor for an Ethiopian student. "
        "Your task is to answer the student's question strictly using the provided COURSE MATERIAL CONTEXT below. "
        "If the context does not contain the answer, say 'I cannot find the answer in the provided course materials.' "
        "Do not hallucinate or use outside knowledge unless it is general background knowledge required to explain the context. "
        "Format your answer beautifully using Markdown (bolding, lists, and clear paragraphs)."
    )
    
    prompt = f"COURSE MATERIAL CONTEXT:\n{context}\n\nSTUDENT QUESTION:\n{question}\n\nANSWER:"
    
    try:
        # Route to Gemini
        if "gemini" in model_id:
            if not settings.GEMINI_API_KEY:
                return "Error: GEMINI_API_KEY is missing."
            
            # Gemini models don't use strict system/user roles in the same way for generate_content (unless using chat context)
            # But in new versions of the SDK, you can provide system_instruction
            model = genai.GenerativeModel(
                model_name=model_id.replace("gemini/", ""),
                system_instruction=system_prompt
            )
            response = model.generate_content(prompt)
            return response.text
            
        # Route to Groq (Llama)
        elif "groq" in model_id:
            if not settings.GROQ_API_KEY:
                return "Error: GROQ_API_KEY is missing."
                
            completion = groq_client.chat.completions.create(
                model=model_id.replace("groq/", ""),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048,
            )
            return completion.choices[0].message.content
            
        else:
            return f"Error: Unknown model provider {model_id}"
            
    except Exception as e:
        print(f"Error generating answer with {model_id}: {e}")
        return f"An error occurred while generating the answer: {str(e)}"
