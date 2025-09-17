from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_TITLE: str
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALG: str
    TELEGRAM_BOT_TOKEN: str
    PUBLIC_BASE_URL: str
    TELEGRAM_WEBHOOK_PATH: str = "/telegram/webhook"
    TELEGRAM_WEBHOOK_SECRET: str = Field(min_length=16)

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
