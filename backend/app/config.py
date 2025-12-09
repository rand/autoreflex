from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./autoreflex.db"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    LOG_LEVEL: str = "INFO"
    
    # Feature Flags
    USE_REAL_OPTIMIZER: bool = False
    AUTOREFLEX_AGENT_CMD: List[str] = [] # Default to empty list (simulator)

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
