# app/services/credits_service.py

from typing import Optional

from sqlalchemy import select, update

from app.services.user_service import get_user_profile
from app.db.postgres import AsyncSessionLocal
from app.db.models import User


async def get_balance(user_id: int) -> int:
    """
    Возвращает текущий баланс сообщений.
    """
    profile = await get_user_profile(user_id)
    return profile.get("credits_balance", 0) if profile else 0


async def add(user_id: int, amount: int) -> None:
    """
    Добавляет сообщения пользователю.
    """
    async with AsyncSessionLocal() as session:
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(messages_balance=User.messages_balance + amount)
        )
        await session.execute(stmt)
        await session.commit()


async def deduct(user_id: int, amount: int) -> bool:
    """
    Списывает сообщения у пользователя.
    Возвращает True, если успешно.
    """
    async with AsyncSessionLocal() as session:
        # читаем текущий баланс
        stmt = select(User.messages_balance).where(User.user_id == user_id)
        result = await session.execute(stmt)
        row = result.first()

        if not row or row[0] < amount:
            return False

        upd = (
            update(User)
            .where(User.user_id == user_id)
            .values(messages_balance=User.messages_balance - amount)
        )
        await session.execute(upd)
        await session.commit()
        return True
