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
        case_sensitive=True, 
        extra="ignore"
    )

    ENVIRONMENT: Literal["development", "production"] = "development"

    SECRET_KEY: str 
         
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS: int
    GROQ_API_KEY: str
 
 
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str 
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "lms"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn: 
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

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
