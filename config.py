from typing import Any, Dict, Optional
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "your_secret_key"  # в продакшн должен быть защищен
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True

settings = Settings()