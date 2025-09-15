from fastapi import FastAPI
from tasks.api.routers import api_router
from tasks.services.logger import logger
from tasks.core.config import settings
from tasks.services.scheduler import setup_scheduler

app = FastAPI(title=settings.APP_TITLE)
app.include_router(api_router)
setup_scheduler(app)

@app.get("/health")
async def health():
    logger.info("health", extra={"action": "health"})
    return {"status": "ok"}
