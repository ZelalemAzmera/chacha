from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Chacha API"
    VERSION: str = "1.0.0"
    
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
