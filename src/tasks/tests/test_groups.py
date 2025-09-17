import pytest
from sqlalchemy import select

from tasks.core.db import SessionLocal
from tasks.core.enums import UserRole
from tasks.db.models.user import User


@pytest.mark.asyncio
async def test_create_group_and_add_student(client, db_session):
    r_admin = await client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "admin1",
            "username": "a1",
            "full_name": "Admin One",
        },
    )
    admin_token = r_admin.json()["access_token"]
    async with db_session as s:
        res = await s.execute(select(User).where(User.telegram_id == "admin1"))
        admin = res.scalar_one()
        admin.role = UserRole.admin
        await s.commit()

    r_teacher = await client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "teach1",
            "username": "t1",
            "full_name": "Teach One",
        },
    )
    async with db_session as s:
        res = await s.execute(select(User).where(User.telegram_id == "teach1"))
        teacher = res.scalar_one()
        teacher.role = UserRole.teacher
        await s.commit()

    r = await client.post(
        "/groups/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "G1", "teacher_id": teacher.id},
    )
    assert r.status_code == 200
    gid = r.json()["id"]

    r_st = await client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "stud1",
            "username": "s1",
            "full_name": "Stud One",
        },
    )
    async with db_session as s:
        res = await s.execute(select(User).where(User.telegram_id == "stud1"))
        student = res.scalar_one()
        await s.commit()

    r2 = await client.post(
        f"/groups/{gid}/add_student",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"student_id": student.id},
    )
    assert r2.status_code == 200
    assert student.id in r2.json()["students"]
