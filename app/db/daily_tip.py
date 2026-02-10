# app/db/daily_tip.py

from datetime import datetime, timezone as dt_timezone
from typing import List, Tuple, Optional

from sqlalchemy import select, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.postgres import AsyncSessionLocal
from app.db.models import DailyTipSettings, AdviceSentLog, User


async def was_advice_sent_today(user_id: int, date_str: str) -> bool:
    """Проверяет, отправляли ли уже совет дня этому пользователю в эту дату."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(AdviceSentLog)
            .where(
                AdviceSentLog.user_id == user_id,
                AdviceSentLog.sent_date == date_str,
            )
        )
        result = await session.scalars(stmt)
        return result.first() is not None


async def mark_advice_sent(user_id: int, date_str: str) -> None:
    """Отмечает, что совет дня отправлен пользователю в эту дату."""
    async with AsyncSessionLocal() as session:
        # UPSERT по (user_id, sent_date)
        stmt = pg_insert(AdviceSentLog).values(
            user_id=user_id,
            sent_date=date_str,
        ).on_conflict_do_nothing(
            index_elements=[AdviceSentLog.user_id, AdviceSentLog.sent_date]
        )
        await session.execute(stmt)
        await session.commit()


async def get_users_enabled_for_advice() -> List[Tuple[int, str, Optional[str], Optional[str], Optional[str]]]:
    """
    Возвращает (user_id, first_name, time_from, time_to, timezone)
    для всех с включённым советом дня.
    """
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                DailyTipSettings.user_id,
                User.first_name,
                DailyTipSettings.time_from,
                DailyTipSettings.time_to,
                DailyTipSettings.timezone,
            )
            .join(User, User.user_id == DailyTipSettings.user_id, isouter=True)
            .where(DailyTipSettings.enabled.is_(True))
        )
        result = await session.execute(stmt)
        rows = result.all()

    res: List[Tuple[int, str, Optional[str], Optional[str], Optional[str]]] = []
    for user_id, first_name, time_from, time_to, timezone in rows:
        res.append(
            (
                user_id,
                first_name or "Друг",
                time_from,
                time_to,
                timezone,
            )
        )
    return res


async def upsert_daily_tip_settings_db(
    user_id: int,
    enabled: bool,
    time_from: Optional[str],
    time_to: Optional[str],
    tz: Optional[str],
) -> dict:
    async with AsyncSessionLocal() as session:
        now = datetime.now(dt_timezone.utc).isoformat()

        stmt = pg_insert(DailyTipSettings).values(
            user_id=user_id,
            enabled=enabled,
            time_from=time_from,
            time_to=time_to,
            timezone=tz,
            updated_at=now,
        ).on_conflict_do_update(
            index_elements=[DailyTipSettings.user_id],
            set_={
                "enabled": enabled,
                "time_from": time_from,
                "time_to": time_to,
                "timezone": tz,
                "updated_at": now,
            },
        )

        await session.execute(stmt)
        await session.commit()

        sel = select(DailyTipSettings).where(DailyTipSettings.user_id == user_id)
        result = await session.scalars(sel)
        row = result.first()

    return {
        "user_id": row.user_id,
        "enabled": bool(row.enabled),
        "time_from": row.time_from,
        "time_to": row.time_to,
        "timezone": row.timezone,
        "updated_at": row.updated_at,
    }
