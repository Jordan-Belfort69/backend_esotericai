# app/services/activity_service.py

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from app.db.postgres import AsyncSessionLocal
from app.db.models import User
from app.services.tasks_service import set_task_progress

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


async def register_daily_activity(user_id: int) -> None:
    """
    Регистрирует активность пользователя за текущий день (по МСК).
    Любое сообщение боту (кроме /start) вызывает эту функцию.
    В день учитываем максимум 1 активность.
    Обновляет стрик и задачи D_3/D_4/D_5.
    """
    today = datetime.now(MOSCOW_TZ).date()
    today_str = today.isoformat()

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.user_id == user_id)
        res = await session.scalars(stmt)
        user = res.first()

        if user is None:
            return

        last_str = user.last_active_date
        streak = user.streak_days or 0

        if last_str == today_str:
            # уже учитывали активность за сегодня
            return

        if last_str is None:
            # первая активность
            streak = 1
        else:
            try:
                last_date = datetime.fromisoformat(last_str).date()
            except ValueError:
                # на всякий пожарный, если там что-то не то
                last_date = today

            if today == last_date + timedelta(days=1):
                # продолжаем стрик
                streak = streak + 1
            else:
                # был пропуск хотя бы одного дня — начинаем новый стрик
                streak = 1

        user.last_active_date = today_str
        user.streak_days = streak

        session.add(user)
        await session.commit()

    # Обновляем прогресс задач активности по стрику
    await set_task_progress(user_id, "D_3", min(streak, 7))
    await set_task_progress(user_id, "D_4", min(streak, 14))
    await set_task_progress(user_id, "D_5", min(streak, 30))
