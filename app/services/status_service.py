# app/services/status_service.py
from typing import Dict, Any
from app.services.user_service import get_user_profile
from core.config import LEVELS

def get_status(user_id: int) -> Dict[str, Any]:
    """
    Возвращает статус пользователя:
    - текущий уровень
    - код уровня
    - название уровня
    - текущий XP
    - следующий уровень
    - осталось до следующего уровня
    """
    profile = get_user_profile(user_id)
    xp = profile.get("xp", 0)
    
    # Определяем текущий уровень
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
    
    # Определяем следующий уровень
    next_level = None
    for i, lvl in enumerate(LEVELS):
        if lvl["code"] == current_level["code"] and i < len(LEVELS) - 1:
            next_level = LEVELS[i + 1]
            break
    
    # Расчитываем оставшийся XP
    remaining_xp = 0
    if next_level:
        remaining_xp = next_level["min_xp"] - xp
    
    return {
        "status_code": current_level["code"],
        "status_title": current_level["title"],
        "xp": xp,
        "next_level_code": next_level["code"] if next_level else None,
        "next_level_title": next_level["title"] if next_level else None,
        "remaining_xp": remaining_xp,
    }

def add_xp(user_id: int, delta: int) -> None:
    """
    Добавляет XP пользователю и проверяет повышение уровня.
    """
    # Здесь будет реализация (пока заглушка)
    pass