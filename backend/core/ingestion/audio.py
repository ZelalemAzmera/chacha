from groq import Groq
from core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def extract_text_from_audio(file_path: str) -> str:
    """
    Transcribes audio to text using Groq's Whisper Large v3 model.
    """
    if not settings.GROQ_API_KEY:
        print("Warning: GROQ_API_KEY is missing. Audio transcription will fail.")
        return ""
        
    try:
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(file_path, audio_file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        return transcription
    except Exception as e:
        print(f"Error transcribing audio {file_path}: {e}")
        return ""
