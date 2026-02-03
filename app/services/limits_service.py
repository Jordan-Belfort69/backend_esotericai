# app/services/limits_service.py

def get_today_limits(user_id: int) -> dict:
    """
    ВРЕМЕННАЯ ЗАГЛУШКА (stub).
    Фронт ожидает структуру с ritual/tarot/horoscope.
    Реальные лимиты будут реализованы позже (если потребуются).
    """
    return {
        "ritual": {"used": 0, "limit": 3},
        "tarot": {"used": 0, "limit": 3},
        "horoscope": {"used": 0, "limit": 3},
    }