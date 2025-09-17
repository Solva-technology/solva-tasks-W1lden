from pydantic import BaseModel


class TelegramCallbackIn(BaseModel):
    telegram_id: str
    username: str | None = None
    full_name: str | None = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
