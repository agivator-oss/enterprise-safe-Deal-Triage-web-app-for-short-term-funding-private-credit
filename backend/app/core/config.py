from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    app_name: str = "Deal Triage"
    api_prefix: str = "/api"

    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/dealtriage"

    storage_root: str = "/data"  # mounted volume in docker-compose

    dev_auth_enabled: bool = True
    dev_auth_default_actor: str = "dev.user@local"

    llm_provider: str = "stub"  # stub | azure

    # Azure OpenAI style
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment: str | None = None

    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2
    llm_no_retention: bool = True

    log_redaction_enabled: bool = True


settings = Settings()
