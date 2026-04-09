from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # LLM
    GEMINI_API_KEY: str = "placeholder"

    # Search
    SERPER_API_KEY: str = "placeholder"

    # YouTube
    YOUTUBE_API_KEY: str = "placeholder"

    # Slack
    SLACK_WEBHOOK_URL: str = "placeholder"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()