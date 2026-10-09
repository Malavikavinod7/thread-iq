from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    project_name: str = "ThreadIQ"
    database_url: str = "postgresql://localhost:5432/threadiq"


    environment: str = "development"
    debug: bool = False

    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    ai_provider: str = "auto"  # 'auto', 'openai', 'gemini', or 'local'
    async_jobs: bool = False  # Set True to dispatch jobs via FastAPI BackgroundTasks


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()