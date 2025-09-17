import pytest
from sqlalchemy import select
from tasks.db.models.user import User
from tasks.core.enums import UserRole
from tasks.db.crud.task import task_crud
from tasks.db.crud.group import group_crud
from tasks.db.crud.user import user_crud
from datetime import datetime, timezone, timedelta
from tasks.services.scheduler import notify_overdue_once

@pytest.mark.asyncio
async def test_overdue_deadline_notifies_all(client, db_session, sent_messages):
    r_admin = await client.post("/auth/telegram/callback", json={"telegram_id": "admin3", "username": "a3", "full_name": "Admin Three"})
    admin_token = r_admin.json()["access_token"]
    async with db_session as s:
        admin = (await s.execute(select(User).where(User.telegram_id == "admin3"))).scalar_one()
        admin.role = UserRole.admin
        await s.commit()

    r_teacher = await client.post("/auth/telegram/callback", json={"telegram_id": "teach3", "username": "t3", "full_name": "Teach Three"})
    r_manager = await client.post("/auth/telegram/callback", json={"telegram_id": "man3", "username": "m3", "full_name": "Man Three"})
    r_student = await client.post("/auth/telegram/callback", json={"telegram_id": "stud3", "username": "s3", "full_name": "Stud Three"})

    async with db_session as s:
        teacher = (await s.execute(select(User).where(User.telegram_id == "teach3"))).scalar_one()
        manager = (await s.execute(select(User).where(User.telegram_id == "man3"))).scalar_one()
        student = (await s.execute(select(User).where(User.telegram_id == "stud3"))).scalar_one()
        teacher.role = UserRole.teacher
        manager.role = UserRole.manager
        await s.commit()

    r_group = await client.post("/groups/", headers={"Authorization": f"Bearer {admin_token}"}, json={"name": "G3", "teacher_id": teacher.id, "manager_id": manager.id})
    gid = r_group.json()["id"]
    await client.post(f"/groups/{gid}/add_student", headers={"Authorization": f"Bearer {admin_token}"}, params={"student_id": student.id})

    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    r_task = await client.post("/tasks/", headers={"Authorization": f"Bearer {admin_token}"}, json={"title": "Overdue", "description": "X", "student_id": student.id, "group_id": gid, "deadline": past})
    tid = r_task.json()["id"]

    sent_messages.clear()
    await notify_overdue_once()
    assert any(c[0] == "stud3" and "Просрочен дедлайн" in c[1] for c in sent_messages)
    assert any(c[0] == "man3" and "Студент просрочил" in c[1] for c in sent_messages)
    assert any(c[0] == "teach3" and "Просрочен дедлайн у студента" in c[1] for c in sent_messages)
