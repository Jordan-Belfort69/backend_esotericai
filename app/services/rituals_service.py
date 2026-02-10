# app/services/rituals_service.py

from typing import Dict, Any, Optional

from sqlalchemy import select

from app.db.postgres import AsyncSessionLocal
from app.db.models import DailyTipSettings
from app.db.daily_tip import upsert_daily_tip_settings_db


async def get_daily_tip_settings(user_id: int) -> Dict[str, Any]:
    """
    Возвращает настройки ежедневного совета для пользователя из Postgres.
    """
    async with AsyncSessionLocal() as session:
        stmt = select(DailyTipSettings).where(DailyTipSettings.user_id == user_id)
        result = await session.scalars(stmt)
        row = result.first()

    if row:
        return {
            "enabled": bool(row.enabled),
            "time_from": row.time_from,
            "time_to": row.time_to,
            "timezone": row.timezone,
            "updated_at": row.updated_at,
        }
    else:
        return {
            "enabled": False,
            "time_from": None,
            "time_to": None,
            "timezone": "Europe/Moscow",
            "updated_at": None,
        }


async def upsert_daily_tip_settings(
    user_id: int,
    enabled: bool,
    time_from: Optional[str],
    time_to: Optional[str],
    tz: Optional[str],
) -> Dict[str, Any]:
    """
    Сохраняет или обновляет настройки ежедневного совета в Postgres.
    """
    return await upsert_daily_tip_settings_db(
        user_id=user_id,
        enabled=enabled,
        time_from=time_from,
        time_to=time_to,
        tz=tz,
    )
