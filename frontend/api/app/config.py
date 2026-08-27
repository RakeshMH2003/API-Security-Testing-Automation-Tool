from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    DATABASE_URL: str = ""
    POSTGRES_URL: str = ""
    POSTGRES_URL_NON_POOLING: str = ""
    POSTGRES_PRISMA_URL: str = ""
    JWT_SECRET: str = "apisec-super-secret-key-change-in-production-2024"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    FRONTEND_URL: str = "*"

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    @property
    def get_database_url(self) -> str:
        url = (
            os.getenv("DATABASE_URL")
            or os.getenv("POSTGRES_URL_NON_POOLING")
            or os.getenv("POSTGRES_URL")
            or os.getenv("POSTGRES_PRISMA_URL")
            or self.DATABASE_URL
            or self.POSTGRES_URL_NON_POOLING
            or self.POSTGRES_URL
        )
        if url:
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            if "sslmode=" in url:
                url = url.replace("sslmode=require", "ssl=require").replace("sslmode=verify-full", "ssl=require").replace("sslmode=prefer", "ssl=prefer")
            return url
        return "sqlite+aiosqlite:////tmp/apisec.db"

settings = Settings()
