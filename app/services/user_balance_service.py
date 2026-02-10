# app/services/user_balance_service.py

from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound

from app.db.postgres import AsyncSessionLocal
from app.db.models import User, UserXP


async def get_messages_balance(user_id: int) -> int:
    """Возвращает текущий баланс сообщений пользователя."""
    async with AsyncSessionLocal() as session:
        stmt = select(User.messages_balance).where(User.user_id == user_id)
        res = await session.execute(stmt)
        row = res.first()
        return int(row[0]) if row and row[0] is not None else 0


async def change_messages_balance(user_id: int, delta: int) -> None:
    """Изменяет баланс сообщений пользователя на указанную величину."""
    if delta == 0:
        return

    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(messages_balance=User.messages_balance + delta)
        )
        await session.execute(stmt)
        await session.commit()


async def get_user_xp(user_id: int) -> int:
    """Возвращает текущий XP пользователя."""
    async with AsyncSessionLocal() as session:
        stmt = select(UserXP.xp).where(UserXP.user_id == user_id)
        res = await session.execute(stmt)
        row = res.first()
        return int(row[0]) if row and row[0] is not None else 0


async def add_user_xp(user_id: int, amount: int) -> None:
    """Добавляет указанный опыт пользователю."""
    if amount <= 0:
        return

    async with AsyncSessionLocal() as session:
        # пробуем найти запись
        stmt = select(UserXP).where(UserXP.user_id == user_id)
        res = await session.scalars(stmt)
        xp_row = res.first()

        if xp_row is None:
            # создаём новую запись
            xp_row = UserXP(user_id=user_id, xp=amount)
            session.add(xp_row)
        else:
            xp_row.xp = (xp_row.xp or 0) + amount

        await session.commit()
