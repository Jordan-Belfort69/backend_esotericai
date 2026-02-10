# app/services/horoscope_service.py

from typing import Literal

from fastapi import HTTPException

from app.services import limits_service, history_service, user_service

ScopeType = Literal["none", "career", "money", "love", "health"]


async def _check_horoscope_limit(user_id: int) -> None:
    """
    Проверяем суточный лимит гороскопов для пользователя.
    Сейчас использует заглушку get_today_limits.
    """
    # get_today_limits пока синхронная, поэтому без await
    limits = limits_service.get_today_limits(user_id)
    info = limits.get("horoscope") or {"used": 0, "limit": 0}
    used = info.get("used", 0)
    limit = info.get("limit", 0)

    if limit is not None and used >= limit:
        raise HTTPException(status_code=429, detail="Horoscope daily limit reached")
    # ВРЕМЕННО: used мы не увеличиваем, потому что это заглушка.


async def _generate_horoscope_text(zodiac: str, scope: ScopeType) -> str:
    """
    ВРЕМЕННО: заглушка генерации гороскопа.
    Потом сюда можно перенести реальный вызов ИИ.
    """
    scope_map = {
        "none": "на общий день",
        "career": "на карьеру",
        "money": "на финансы",
        "love": "на отношения",
        "health": "на здоровье",
    }
    scope_text = scope_map.get(scope, "на общий день")
    return (
        f"Краткий гороскоп для знака {zodiac} {scope_text}. "
        f"Это заглушка — позже здесь будет текст от ИИ."
    )


async def _save_history_record(user_id: int, zodiac: str, scope: ScopeType, text: str) -> None:
    """
    Записываем запрос гороскопа в history.
    type фиксируем как 'horoscope'.
    """
    question = f"Гороскоп: знак={zodiac}, сфера={scope}"
    await history_service.log_event(
        user_id=user_id,
        event_type="horoscope",
        question=question,
        answer_full=text,
    )


async def create_horoscope(user_id: int, zodiac: str, scope: ScopeType) -> str:
    """
    Полный цикл:
    1) проверка лимита,
    2) генерация текста,
    3) запись в history,
    4) возврат текста.
    """
    user = await user_service.get_user_profile(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await _check_horoscope_limit(user_id)

    text = await _generate_horoscope_text(zodiac=zodiac, scope=scope)

    await _save_history_record(user_id=user_id, zodiac=zodiac, scope=scope, text=text)

    return text


def create_horoscope_stub(zodiac: str, scope: str) -> str:
    """
    Заглушка для генерации гороскопа (для использования в API).
    """
    scope_map = {
        "none": "на общий день",
        "career": "на карьеру",
        "money": "на финансы",
        "love": "на отношения",
        "health": "на здоровье",
    }
    scope_text = scope_map.get(scope, "на общий день")
    return (
        f"Краткий гороскоп для знака {zodiac} {scope_text}. "
        f"Это заглушка — позже здесь будет текст от ИИ."
    )
