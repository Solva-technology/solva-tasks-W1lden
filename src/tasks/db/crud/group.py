from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from tasks.db.models.group import Group
from tasks.db.models.user import User

class GroupCRUD:
    async def get_by_name(self, session: AsyncSession, name: str) -> Group | None:
        res = await session.execute(select(Group).where(Group.name == name))
        return res.scalar_one_or_none()

    async def create(self, session: AsyncSession, name: str, manager: User | None, teacher: User | None) -> Group:
        exists = await self.get_by_name(session, name)
        if exists:
            raise ValueError("group_name_exists")
        obj = Group(name=name, manager=manager, teacher=teacher)
        session.add(obj)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("group_name_exists")
        await session.refresh(obj)
        return obj

    async def get(self, session: AsyncSession, group_id: int) -> Group | None:
        stmt = (
            select(Group)
            .options(
                selectinload(Group.students),
                selectinload(Group.manager),
                selectinload(Group.teacher),
            )
            .where(Group.id == group_id)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_groups(self, session: AsyncSession) -> list[Group]:
        stmt = (
            select(Group)
            .options(
                selectinload(Group.students),
                selectinload(Group.manager),
                selectinload(Group.teacher),
            )
            .order_by(Group.id)
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def add_student(self, session: AsyncSession, group: Group, student: User) -> Group:
        if student not in group.students:
            group.students.append(student)
            await session.commit()
            await session.refresh(group)
        return group

group_crud = GroupCRUD()
