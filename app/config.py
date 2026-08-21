from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    database_url: str = "sqlite:///./resume_screener.db"
    match_threshold: int = 7

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
