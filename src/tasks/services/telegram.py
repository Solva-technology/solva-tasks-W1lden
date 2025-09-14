import httpx
from tasks.core.config import settings

class TelegramService:
    def __init__(self):
        self.base = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

    async def send_message(self, chat_id: str, text: str):
        url = f"{self.base}/sendMessage"
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json={"chat_id": chat_id, "text": text})

telegram_service = TelegramService()
