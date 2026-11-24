from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENTOFFICE_", env_file=".env", extra="ignore")

    app_name: str = "AgentOffice"
    secret_key: str = "change-me"
    database_url: str = "postgresql+asyncpg://agentoffice:agentoffice@localhost:5432/agentoffice"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
