import os
from typing import List, Literal
from pathlib import Path
from pydantic import AnyUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Config(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False, 
        extra="ignore"
    )

    ENVIRONMENT: Literal["development", "production"] = "development"

    SECRET_KEY: str 
         
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS: int
    GROQ_API_KEY: str
 
 
    # Database settings - Uses single DATABASE_URL variable
    DATABASE_URL: str = "postgresql+asyncpg://postgres:12345@localhost:5432/lms"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Pydantic reads DATABASE_URL from environment or .env
        url = self.DATABASE_URL
        
        # Ensure correct prefix for asyncpg
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        return url

    API_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"

    BACKEND_CORS_ORIGINS: List[AnyUrl] = []

    MAIL_USERNAME: str 
    MAIL_PASSWORD: str 
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "LMS System"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True



config = Config()
