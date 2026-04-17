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

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DISABLE_OUTBOUND_PROXY: bool
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
