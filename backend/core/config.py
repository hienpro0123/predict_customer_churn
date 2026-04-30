from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseSettings):
    DATABRICKS_URL: str
    DATABRICKS_TOKEN: str
    DATABRICKS_TIMEOUT: int
    DATABRICKS_RETRY_ATTEMPTS: int = 2
    DATABRICKS_RETRY_BACKOFF_SECONDS: float = 1.0

    DISABLE_OUTBOUND_PROXY: bool
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173"

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
