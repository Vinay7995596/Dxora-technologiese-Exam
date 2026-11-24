from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Website Link Analysis API"
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4-mini"
    request_timeout: float = 20.0
    max_html_bytes: int = 2_000_000
    max_text_chars: int = 18_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
