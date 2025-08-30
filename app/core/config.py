import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    JSEARCH_API_KEY: str = os.getenv("JSEARCH_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # API URLs
    JSEARCH_BASE_URL: str = "https://jsearch.p.rapidapi.com"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # Model settings
    LLM_MODEL: str = "gpt-4o"  # or another OpenAI model name
    
    # App settings
    APP_NAME: str = "Resume Align Test"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

settings = Settings() 