from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tasks.core.enums import TaskStatus
from tasks.db.models.group import Group
from tasks.db.models.task import Task
from tasks.db.models.user import User


class TaskCRUD:
    async def create(
        self,
        session: AsyncSession,
        title: str,
        description: str | None,
        status: TaskStatus,
        student: User,
        group: Group,
        deadline,
    ) -> Task:
        obj = Task(
            title=title,
            description=description,
            status=status,
            student=student,
            group=group,
            deadline=deadline,
        )
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get(self, session: AsyncSession, task_id: int) -> Task | None:
        stmt = (
            select(Task)
            .options(
                selectinload(Task.student),
                selectinload(Task.group).selectinload(Group.manager),
            )
            .where(Task.id == task_id)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_status(
        self, session: AsyncSession, task: Task, new_status: TaskStatus
    ) -> Task:
        task.status = new_status
        await session.commit()
        await session.refresh(task)
        return task

    async def list_tasks(
        self,
        session: AsyncSession,
        student_id: int | None,
        group_id: int | None,
        status: TaskStatus | None,
        limit: int | None,
        offset: int | None,
    ) -> list[Task]:
        stmt = select(Task).options(
            selectinload(Task.student),
            selectinload(Task.group),
        )
        if student_id is not None:
            stmt = stmt.where(Task.student_id == student_id)
        if group_id is not None:
            stmt = stmt.where(Task.group_id == group_id)
        if status is not None:
            stmt = stmt.where(Task.status == status)
        stmt = stmt.order_by(Task.id)
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def overdue_without_notice(
        self, session: AsyncSession, now: datetime
    ) -> list[Task]:
        stmt = (
            select(Task)
            .options(
                selectinload(Task.student),
                selectinload(Task.group).selectinload(Group.manager),
            )
            .where(Task.deadline.isnot(None))
            .where(Task.deadline < now)
            .where(
                Task.status.in_(
                    [
                        TaskStatus.new,
                        TaskStatus.in_progress,
                        TaskStatus.submitted,
                    ]
                )
            )
            .where(
                (Task.last_deadline_notice_at.is_(None))
                | (Task.last_deadline_notice_at < Task.deadline)
            )
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def mark_deadline_notified(
        self, session: AsyncSession, task: Task, at: datetime
    ) -> Task:
        task.last_deadline_notice_at = at
        await session.commit()
        await session.refresh(task)
        return task


task_crud = TaskCRUD()
