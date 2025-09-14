from pydantic import BaseModel
from tasks.core.enums import UserRole

class UserOut(BaseModel):
    id: int
    telegram_id: str
    username: str | None
    full_name: str | None
    role: UserRole

    class Config:
        from_attributes = True
