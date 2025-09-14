from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_TITLE: str
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALG: str
    TELEGRAM_BOT_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
