import base64
from groq import Groq
from core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_text_from_image(image_path: str, is_question: bool = False) -> str:
    """
    Uses Groq's Vision model (Llama 3.2 Vision) to perform OCR and extract text.
    If is_question is True, prompts the model to focus on extracting the exact question text.
    """
    if not settings.GROQ_API_KEY:
        print("Warning: GROQ_API_KEY is missing. OCR will fail.")
        return ""
        
    try:
        base64_image = encode_image_to_base64(image_path)
        
        prompt = "Please extract all text from this image exactly as written."
        if is_question:
            prompt = "This is a photo of a student's question. Please extract the question text clearly, preserving any formulas or math equations."

        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error performing OCR on image {image_path}: {e}")
        return ""
