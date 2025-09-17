import httpx

from tasks.core.config import settings


class TelegramService:
    def __init__(self):
        self.base = (
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
        )

    async def send_message(self, chat_id: str, text: str):
        url = f"{self.base}/sendMessage"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                await client.post(url, json={"chat_id": chat_id, "text": text})
            except Exception:
                return

    async def set_webhook(self, url: str, secret: str):
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                await client.post(
                    f"{self.base}/setWebhook",
                    json={
                        "url": url,
                        "secret_token": secret,
                        "drop_pending_updates": True,
                    },
                )
            except Exception:
                return


telegram_service = TelegramService()
