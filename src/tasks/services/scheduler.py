import os
import asyncio
import contextlib
from datetime import datetime, timezone
from fastapi import FastAPI
from tasks.core.constants import NOTIFY_INTERVAL, DEADLINE_GRACE
from tasks.core.db import SessionLocal
from tasks.db.crud.task import task_crud
from tasks.services.telegram import telegram_service
from tasks.services.logger import logger

ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"

async def notify_overdue_once():
    now = datetime.now(timezone.utc)
    async with SessionLocal() as session:
        items = await task_crud.overdue_without_notice(session, now - DEADLINE_GRACE)
        for t in items:
            if t.student and t.student.telegram_id:
                await telegram_service.send_message(t.student.telegram_id, f"Просрочен дедлайн задачи: {t.title}")
            if t.group and t.group.manager and t.group.manager.telegram_id:
                await telegram_service.send_message(t.group.manager.telegram_id, f"Студент просрочил задачу: {t.title}")
            if t.group and t.group.teacher and t.group.teacher.telegram_id:
                name = t.student.full_name or t.student.username or t.student.telegram_id
                await telegram_service.send_message(t.group.teacher.telegram_id, f"Просрочен дедлайн у студента {name}: {t.title}")
            await task_crud.mark_deadline_notified(session, t, now)
            logger.info("deadline_notice_sent", extra={"action": "deadline_notice_sent", "task_id": t.id})

def setup_scheduler(app: FastAPI):
    if not ENABLE_SCHEDULER:
        return

    holder = {"task": None}

    async def runner():
        try:
            while True:
                try:
                    await notify_overdue_once()
                except Exception as e:
                    logger.error("deadline_loop_error", extra={"action": "deadline_loop_error", "error": str(e)})
                await asyncio.sleep(NOTIFY_INTERVAL.total_seconds())
        except asyncio.CancelledError:
            return

    @app.on_event("startup")
    async def _start():
        holder["task"] = asyncio.create_task(runner())

    @app.on_event("shutdown")
    async def _stop():
        t = holder["task"]
        if t and not t.cancelled():
            t.cancel()
            with contextlib.suppress(Exception):
                await t
