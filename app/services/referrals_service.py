# app/services/referrals_service.py

from typing import Dict, Any, List, Optional

from sqlalchemy import select

from app.db.postgres import AsyncSessionLocal
from app.db.models import User
from app.services.tasks_service import increment_task_progress


# === НАСТРОЙКА: замени на имя твоего бота ===
BOT_USERNAME = "ai_esoterictestbot"  # ← Уже правильно!


def generate_ref_code() -> str:
    """Генерирует уникальный реферальный код."""
    import random
    import string

    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


async def get_or_create_ref_code(user_id: int) -> str:
    """Получает или создаёт реферальный код для пользователя."""
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.scalars(stmt)
        user = result.first()

        if user is None:
            raise ValueError(f"User {user_id} not found")

        if user.ref_code:
            return user.ref_code

        ref_code = generate_ref_code()
        user.ref_code = ref_code
        await session.commit()
        return ref_code


async def get_referrals_info(user_id: int) -> Dict[str, Any]:
    """Возвращает данные для /api/referrals/info по фронтовому контракту."""
    ref_code = await get_or_create_ref_code(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start={ref_code}"

    async with AsyncSessionLocal() as session:
        stmt = (
            select(User.first_name, User.username, User.created_at)
            .where(User.referrer_id == user_id)
            .order_by(User.created_at.desc())
        )
        result = await session.execute(stmt)
        rows = result.all()

    friends: List[Dict[str, Any]] = []
    for first_name, username, created_at in rows:
        name = first_name or username or "Друг"
        friends.append(
            {
                "name": name,
                "joined_at": created_at,
                "bonus_credits": 0,
                "status": "joined",
            }
        )

    return {
        "referral_link": referral_link,
        "friends": friends,
    }


async def apply_referral_code(current_user_id: int, ref_code: str) -> Optional[int]:
    """
    Применяет реферальный код к текущему пользователю.
    Возвращает referrer_id, если успешно, иначе None.
    """
    if not ref_code:
        return None

    async with AsyncSessionLocal() as session:
        # находим реферера по коду
        stmt = select(User).where(User.ref_code == ref_code)
        result = await session.scalars(stmt)
        referrer = result.first()
        if not referrer:
            return None

        # нельзя быть рефералом самому у себя
        if referrer.user_id == current_user_id:
            return None

        # находим текущего пользователя
        stmt2 = select(User).where(User.user_id == current_user_id)
        result2 = await session.scalars(stmt2)
        user = result2.first()
        if not user:
            return None

        # уже есть реферер — ничего не делаем
        if user.referrer_id:
            return None

        user.referrer_id = referrer.user_id
        await session.commit()

    # после успешной привязки — двигаем задания реферера
    await increment_task_progress(referrer.user_id, "REF_1")
    await increment_task_progress(referrer.user_id, "REF_2")
    await increment_task_progress(referrer.user_id, "REF_3")
    await increment_task_progress(referrer.user_id, "REF_4")
    await increment_task_progress(referrer.user_id, "REF_5")

    return referrer.user_id
