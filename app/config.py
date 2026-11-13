from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Eleven"
    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"

    api_access_token: str | None = Field(default=None, validation_alias="ELEVEN_API_TOKEN")
    owner_profile_id: str = Field(default="owner", validation_alias="OWNER_PROFILE_ID")

    llm_api_key: str | None = Field(default=None, validation_alias="LLM_API_KEY")
    llm_base_url: str = Field(default="https://api.openai.com", validation_alias="LLM_BASE_URL")
    llm_model: str | None = Field(default=None, validation_alias="LLM_MODEL")
    llm_timeout_seconds: float = Field(default=45.0, validation_alias="LLM_TIMEOUT_SECONDS", gt=0, le=180)

    github_token: str | None = Field(default=None, validation_alias="GITHUB_TOKEN")
    github_repository: str | None = Field(default=None, validation_alias="GITHUB_REPOSITORY")
    github_base_branch: str = Field(default="main", validation_alias="GITHUB_BASE_BRANCH")

    database_path: Path = Field(default=Path("./data/eleven.db"), validation_alias="DATABASE_PATH")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
