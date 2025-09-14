from fastapi import FastAPI
from tasks.api.routers import api_router
from tasks.services.logger import logger
from tasks.core.config import settings

app = FastAPI(title=settings.APP_TITLE)
app.include_router(api_router)

@app.get("/health")
async def health():
    logger.info("health", extra={"action": "health"})
    return {"status": "ok"}
