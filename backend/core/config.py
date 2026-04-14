from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseSettings):
    DATABRICKS_URL: str
    DATABRICKS_TOKEN: str
    DATABRICKS_TIMEOUT: int

    GEMINI_API_KEY: str
    GEMINI_API_KEYS: str = ""
    GEMINI_MODEL: str
    GEMINI_TIMEOUT: int
    FAST_PREDICTION_MODE: bool = False

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DISABLE_OUTBOUND_PROXY: bool

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
    def gemini_api_key_pool(self) -> list[str]:
        keys = [self.GEMINI_API_KEY, *(part.strip() for part in self.GEMINI_API_KEYS.split(","))]
        unique_keys: list[str] = []
        for key in keys:
            if key and key not in unique_keys:
                unique_keys.append(key)
        return unique_keys


settings = Settings()
