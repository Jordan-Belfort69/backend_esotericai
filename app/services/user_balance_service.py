# app/services/user_balance_service.py

from sqlalchemy import select, update

from app.db.postgres import AsyncSessionLocal
from app.db.models import User, UserXP, UserTask
from app.services.tasks_service import increment_task_progress, TASK_CONFIG


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
    """
    Добавляет указанный опыт пользователю
    и обновляет задачи уровней LEVEL_UP_*.
    """
    if amount <= 0:
        return

    # 1. Обновляем XP в таблице user_xp
    async with AsyncSessionLocal() as session:
        stmt = select(UserXP).where(UserXP.user_id == user_id)
        res = await session.scalars(stmt)
        xp_row = res.first()

        if xp_row is None:
            new_xp = amount
            xp_row = UserXP(user_id=user_id, xp=new_xp)
            session.add(xp_row)
        else:
            new_xp = (xp_row.xp or 0) + amount
            xp_row.xp = new_xp

        await session.commit()

    # 2. Обновляем задачи уровней
    level_tasks = [
        "LEVEL_UP_1",
        "LEVEL_UP_2",
        "LEVEL_UP_3",
        "LEVEL_UP_4",
        "LEVEL_UP_5",
        "LEVEL_UP_6",
    ]

    for code in level_tasks:
        cfg = TASK_CONFIG.get(code)
        if not cfg:
            continue

        threshold = cfg["progress_target"]  # порог XP для этого уровня

        # a) гарантируем наличие записи задачи
        await increment_task_progress(user_id, code, delta=0)

        # b) синхронизируем progress_current с текущим XP
        async with AsyncSessionLocal() as session:
            stmt = (
                update(UserTask)
                .where(
                    UserTask.user_id == user_id,
                    UserTask.task_code == code,
                )
                .values(progress_current=new_xp, progress_target=threshold)
                .returning(UserTask.progress_current, UserTask.progress_target, UserTask.reward_claimed)
            )
            res = await session.execute(stmt)
            row = res.first()
            await session.commit()

        if not row:
            continue

        progress_current, progress_target, reward_claimed = row

        # c) если порог достигнут и награда ещё не выдана — триггерим её
        if (not reward_claimed) and progress_current >= progress_target:
            await increment_task_progress(user_id, code, delta=0)
