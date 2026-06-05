import os
import tempfile
from moviepy.editor import VideoFileClip
from core.ingestion.audio import extract_text_from_audio

def extract_text_from_video(file_path: str) -> str:
    """
    Extracts audio from video and transcribes it using Whisper.
    """
    try:
        # Load video
        video = VideoFileClip(file_path)
        
        # Check if video has audio
        if video.audio is None:
            return "No audio track found in video."
            
        # Create a temporary file for the extracted audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
            
        # Write audio to the temp file
        video.audio.write_audiofile(temp_audio_path, logger=None)
        video.close()
        
        # Transcribe audio
        text = extract_text_from_audio(temp_audio_path)
        
        # Cleanup temp file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            
        return text
    except Exception as e:
        print(f"Error extracting text from video {file_path}: {e}")
        return ""
