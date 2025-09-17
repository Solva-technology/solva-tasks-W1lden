from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.core.enums import UserRole
from tasks.db.models.user import User


class UserCRUD:
    async def get_by_id(
        self, session: AsyncSession, user_id: int
    ) -> User | None:
        res = await session.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none()

    async def get_by_telegram(
        self, session: AsyncSession, telegram_id: str
    ) -> User | None:
        res = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return res.scalar_one_or_none()

    async def create_or_update_telegram(
        self,
        session: AsyncSession,
        telegram_id: str,
        username: str | None,
        full_name: str | None,
    ) -> User:
        user = await self.get_by_telegram(session, telegram_id)
        if user:
            user.username = username
            user.full_name = full_name
            await session.commit()
            await session.refresh(user)
            return user
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            role=UserRole.student,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


user_crud = UserCRUD()
