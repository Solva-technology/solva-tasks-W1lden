import pytest
from sqlalchemy import select

from tasks.core.enums import UserRole
from tasks.db.models.user import User


@pytest.mark.asyncio
async def test_student_cannot_create_group_or_task(client, db_session):
    r_student = await client.post(
        "/auth/telegram/callback",
        json={"telegram_id": "studx", "username": "sx", "full_name": "Stud X"},
    )
    token = r_student.json()["access_token"]

    r_g = await client.post(
        "/groups/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "GX"},
    )
    assert r_g.status_code == 403

    r_admin = await client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "adminx",
            "username": "ax",
            "full_name": "Admin X",
        },
    )
    admin_token = r_admin.json()["access_token"]
    async with db_session as s:
        admin = (
            await s.execute(select(User).where(User.telegram_id == "adminx"))
        ).scalar_one()
        admin.role = UserRole.admin
        await s.commit()

    await client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "teachx",
            "username": "tx",
            "full_name": "Teach X",
        },
    )
    async with db_session as s:
        teacher = (
            await s.execute(select(User).where(User.telegram_id == "teachx"))
        ).scalar_one()
        teacher.role = UserRole.teacher
        await s.commit()

    r_g2 = await client.post(
        "/groups/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "GX2", "teacher_id": teacher.id},
    )
    gid = r_g2.json()["id"]

    r_t = await client.post(
        "/tasks/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Nope", "student_id": 1, "group_id": gid},
    )
    assert r_t.status_code in (401, 403)
