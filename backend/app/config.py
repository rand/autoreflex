from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./autoreflex.db"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
