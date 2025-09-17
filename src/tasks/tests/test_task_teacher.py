import pytest
from sqlalchemy import select

from tasks.core.enums import UserRole
from tasks.db.models.user import User


@pytest.mark.asyncio
async def test_task_create_by_teacher(client, db_session, sent_messages):
    r_teacher = await client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "teachA",
            "username": "teacherA",
            "full_name": "Teach A",
        },
    )
    teacher_token = r_teacher.json()["access_token"]
    async with db_session as s:
        teacher = (
            await s.execute(select(User).where(User.telegram_id == "teachA"))
        ).scalar_one()
        teacher.role = UserRole.teacher
        await s.commit()

    r_manager = await client.post(
        "/auth/telegram/callback",
        json={"telegram_id": "manA", "username": "manA", "full_name": "Man A"},
    )
    async with db_session as s:
        manager = (
            await s.execute(select(User).where(User.telegram_id == "manA"))
        ).scalar_one()
        manager.role = UserRole.manager
        await s.commit()

    r_group = await client.post(
        "/groups/",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "name": "GT",
            "teacher_id": teacher.id,
            "manager_id": manager.id,
        },
    )
    gid = r_group.json()["id"]

    r_student = await client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "studA",
            "username": "studA",
            "full_name": "Stud A",
        },
    )
    async with db_session as s:
        student = (
            await s.execute(select(User).where(User.telegram_id == "studA"))
        ).scalar_one()
        await s.commit()

    await client.post(
        f"/groups/{gid}/add_student",
        headers={"Authorization": f"Bearer {teacher_token}"},
        params={"student_id": student.id},
    )

    sent_messages.clear()
    r_task = await client.post(
        "/tasks/",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "title": "ByTeacher",
            "description": "X",
            "student_id": student.id,
            "group_id": gid,
        },
    )
    assert r_task.status_code == 200
    assert any(
        c[0] == "studA" and "Новая задача" in c[1] for c in sent_messages
    )
