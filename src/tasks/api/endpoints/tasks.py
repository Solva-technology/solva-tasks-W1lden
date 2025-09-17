from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.api.deps import get_current_user, get_db, require_roles
from tasks.api.schemas.task import TaskCreateIn, TaskOut, TaskPatchIn
from tasks.core.constants import PAGE_SIZE_DEFAULT, PAGE_SIZE_MAX
from tasks.core.enums import TaskStatus, UserRole
from tasks.db.crud.group import group_crud
from tasks.db.crud.task import task_crud
from tasks.db.crud.user import user_crud
from tasks.services.logger import logger
from tasks.services.telegram import telegram_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut)
async def create_task(
    payload: TaskCreateIn,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_roles(UserRole.admin, UserRole.teacher)),
):
    student = await user_crud.get_by_id(db, payload.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    group = await group_crud.get(db, payload.group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await task_crud.create(
        db,
        payload.title,
        payload.description,
        TaskStatus.new,
        student,
        group,
        payload.deadline,
    )
    if student.telegram_id:
        await telegram_service.send_message(
            student.telegram_id, f"Новая задача: {obj.title}"
        )
    logger.info(
        "task_created",
        extra={
            "extra": {
                "user_id": student.id,
                "action": "task_created",
                "task_id": obj.id,
            }
        },
    )
    return obj


@router.get("/", response_model=list[TaskOut])
async def list_tasks(
    student_id: int | None = None,
    group_id: int | None = None,
    status: TaskStatus | None = Query(default=None),
    limit: int = Query(default=PAGE_SIZE_DEFAULT, ge=1, le=PAGE_SIZE_MAX),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current=Depends(get_current_user),
):
    if current.role == UserRole.student:
        student_id = current.id
    items = await task_crud.list_tasks(
        db, student_id, group_id, status, limit, offset
    )
    return items


@router.get("/{task_id}", response_model=TaskOut)
async def task_detail(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current=Depends(get_current_user),
):
    obj = await task_crud.get(db, task_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if current.role == UserRole.student and obj.student_id != current.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return obj


@router.patch("/{task_id}", response_model=TaskOut)
async def patch_task(
    task_id: int,
    payload: TaskPatchIn,
    db: AsyncSession = Depends(get_db),
    current=Depends(get_current_user),
):
    obj = await task_crud.get(db, task_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if current.role in {UserRole.admin, UserRole.teacher}:
        updated = obj
        if payload.title is not None:
            updated.title = payload.title
        if payload.description is not None:
            updated.description = payload.description
        if payload.deadline is not None:
            updated.deadline = payload.deadline
        if payload.status is not None:
            old_status = obj.status
            updated = await task_crud.update_status(db, obj, payload.status)
            if updated.group.manager and updated.group.manager.telegram_id:
                await telegram_service.send_message(
                    updated.group.manager.telegram_id,
                    f"Статус задачи {updated.id}: {old_status} → {updated.status}",
                )
            logger.info(
                "task_status_changed",
                extra={
                    "extra": {
                        "user_id": current.id,
                        "action": "task_status_changed",
                        "task_id": updated.id,
                        "old_status": str(old_status),
                        "new_status": str(updated.status),
                    }
                },
            )
        else:
            await db.commit()
            await db.refresh(updated)
        return updated
    if current.role == UserRole.student:
        if obj.student_id != current.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        if payload.status is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        old_status = obj.status
        updated = await task_crud.update_status(db, obj, payload.status)
        if updated.group.manager and updated.group.manager.telegram_id:
            await telegram_service.send_message(
                updated.group.manager.telegram_id,
                f"Статус задачи {updated.id}: {old_status} → {updated.status}",
            )
        logger.info(
            "task_status_changed",
            extra={
                "extra": {
                    "user_id": current.id,
                    "action": "task_status_changed",
                    "task_id": updated.id,
                    "old_status": str(old_status),
                    "new_status": str(updated.status),
                }
            },
        )
        return updated
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
