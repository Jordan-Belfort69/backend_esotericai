# app/services/user_balance_service.py

from sqlalchemy import select, update

from app.db.postgres import AsyncSessionLocal
from app.db.models import User, UserXP


async def get_messages_balance(user_id: int) -> int:
    async with AsyncSessionLocal() as session:
        stmt = select(User.messages_balance).where(User.user_id == user_id)
        res = await session.execute(stmt)
        row = res.first()
        return int(row[0]) if row and row[0] is not None else 0


async def change_messages_balance(user_id: int, delta: int) -> None:
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
    async with AsyncSessionLocal() as session:
        stmt = select(UserXP.xp).where(UserXP.user_id == user_id)
        res = await session.execute(stmt)
        row = res.first()
        return int(row[0]) if row and row[0] is not None else 0


async def add_user_xp(user_id: int, amount: int) -> None:
    if amount <= 0:
        return

    async with AsyncSessionLocal() as session:
        stmt = select(UserXP).where(UserXP.user_id == user_id)
        res = await session.scalars(stmt)
        xp_row = res.first()

        if xp_row is None:
            xp_row = UserXP(user_id=user_id, xp=amount)
            session.add(xp_row)
        else:
            xp_row.xp = (xp_row.xp or 0) + amount

        await session.commit()
