"""Configuration settings for the backend API."""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    clinicaltrials_api_base: str = "https://clinicaltrials.gov/api/v2"
    
    class Config:
        env_file = ".env"


settings = Settings()

