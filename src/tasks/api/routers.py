from fastapi import APIRouter

from tasks.api.endpoints import auth, groups, tasks, telegram, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(groups.router)
api_router.include_router(tasks.router)
api_router.include_router(telegram.router)
