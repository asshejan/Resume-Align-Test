import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    JSEARCH_API_KEY: str = os.getenv("JSEARCH_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # API URLs
    JSEARCH_BASE_URL: str = "https://jsearch.p.rapidapi.com"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Model settings
    LLM_MODEL: str = "openai/gpt-4o-mini"
    
    # App settings
    APP_NAME: str = "Resume Align Test"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

settings = Settings() 