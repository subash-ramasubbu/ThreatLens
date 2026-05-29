from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "ThreatLens"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@127.0.0.1:5455/threatlens")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    ABUSEIPDB_API_KEY: str = ""
    ALIENVAULT_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()