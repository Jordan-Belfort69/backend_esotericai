# app/services/status_service.py

from typing import Dict, Any

from app.services.user_service import get_user_profile
from core.config import LEVELS


async def get_status(user_id: int) -> Dict[str, Any]:
    """
    Возвращает статус пользователя:
    - текущий уровень
    - код уровня
    - название уровня
    - текущий XP
    - следующий уровень
    - осталось до следующего уровня
    """
    profile = await get_user_profile(user_id)
    if not profile:
        # пользователь ещё не создан, считаем базовые значения
        xp = 0
    else:
        xp = profile.get("xp", 0)

    current_level = LEVELS[0]
    for lvl in LEVELS:
        min_xp = lvl["min_xp"]
        max_xp = lvl["max_xp"]
        if max_xp is None:
            if xp >= min_xp:
                current_level = lvl
            break
        if min_xp <= xp <= max_xp:
            current_level = lvl
            break

    next_level = None
    for i, lvl in enumerate(LEVELS):
        if lvl["code"] == current_level["code"] and i < len(LEVELS) - 1:
            next_level = LEVELS[i + 1]
            break

    remaining_xp = 0
    if next_level:
        remaining_xp = max(next_level["min_xp"] - xp, 0)

    return {
        "status_code": current_level["code"],
        "status_title": current_level["title"],
        "xp": xp,
        "next_level_code": next_level["code"] if next_level else None,
        "next_level_title": next_level["title"] if next_level else None,
        "remaining_xp": remaining_xp,
    }


async def add_xp(user_id: int, delta: int) -> None:
    """
    Добавляет XP пользователю и проверяет повышение уровня.
    Реализацию сделаем, когда будем переносить логику user_xp.
    """
    # пока заглушка, чтобы интерфейс был async
    return None
