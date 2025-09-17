from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from tasks.core.enums import UserRole
from tasks.db.models.user import User


@pytest.mark.asyncio
async def test_task_create_and_status_flow(client, db_session, sent_messages):
    r_admin = await client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "admin2",
            "username": "a2",
            "full_name": "Admin Two",
        },
    )
    admin_token = r_admin.json()["access_token"]
    async with db_session as s:
        admin = (
            await s.execute(select(User).where(User.telegram_id == "admin2"))
        ).scalar_one()
        admin.role = UserRole.admin
        await s.commit()

    await client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "teach2",
            "username": "t2",
            "full_name": "Teach Two",
        },
    )
    await client.post(
        "/auth/telegram/callback",
        json={"telegram_id": "man2", "username": "m2", "full_name": "Man Two"},
    )
    async with db_session as s:
        teacher = (
            await s.execute(select(User).where(User.telegram_id == "teach2"))
        ).scalar_one()
        manager = (
            await s.execute(select(User).where(User.telegram_id == "man2"))
        ).scalar_one()
        teacher.role = UserRole.teacher
        manager.role = UserRole.manager
        await s.commit()

    r_group = await client.post(
        "/groups/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "G2",
            "teacher_id": teacher.id,
            "manager_id": manager.id,
        },
    )
    gid = r_group.json()["id"]

    r_student = await client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "stud2",
            "username": "s2",
            "full_name": "Stud Two",
        },
    )
    student_token = r_student.json()["access_token"]
    async with db_session as s:
        student = (
            await s.execute(select(User).where(User.telegram_id == "stud2"))
        ).scalar_one()
        await s.commit()

    r_add = await client.post(
        f"/groups/{gid}/add_student",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"student_id": student.id},
    )
    assert r_add.status_code == 200

    sent_messages.clear()
    deadline = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    r_task = await client.post(
        "/tasks/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "T2",
            "description": "D",
            "student_id": student.id,
            "group_id": gid,
            "deadline": deadline,
        },
    )
    assert r_task.status_code == 200
    assert any(
        c[0] == "stud2" and "Новая задача" in c[1] for c in sent_messages
    )

    r_list = await client.get(
        "/tasks/", headers={"Authorization": f"Bearer {student_token}"}
    )
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 1

    sent_messages.clear()
    tid = r_task.json()["id"]
    r_patch = await client.patch(
        f"/tasks/{tid}",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"status": "сдана"},
    )
    assert r_patch.status_code == 200
    assert any(
        c[0] == "man2" and "Статус задачи" in c[1] for c in sent_messages
    )
