from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ThreatLens"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/threatlens"
    REDIS_URL: str = "redis://localhost:6379"

    ABUSEIPDB_API_KEY: str = ""
    ALIENVAULT_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()