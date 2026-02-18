# app/api/me.py

import logging

from fastapi import APIRouter, HTTPException, status
from app.deps.current_user import CurrentUserDep
from app.services.user_service import get_user_profile
from app.services.tasks_service import increment_task_progress
from app.services.subscription_service import check_and_complete_subscriptions
from bot_main import bot

router = APIRouter(prefix="/api")


@router.get("/me")
async def get_me(
    user_id: CurrentUserDep,
):
    """
    Возвращает профиль пользователя с полным статусом.
    При каждом запуске мини-аппа автоматически проверяет подписки.
    """
    # Проверка подписок (D_1, D_2)
    try:
        await check_and_complete_subscriptions(bot, user_id)
    except Exception as e:
        logging.exception("Failed to check subscriptions in /api/me: %s", e)

    # Ежедневный вход (D_DAILY)
    try:
        await increment_task_progress(user_id, "D_DAILY")
    except Exception as e:
        logging.exception("Failed to increment D_DAILY in /api/me: %s", e)

    profile = await get_user_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return {
        "user_id": user_id,
        "name": profile["name"],
        "username": profile["username"],
        "photo_url": profile["photo_url"],
        "registered_at": profile["registered_at"],
        "status_code": profile["status_code"],
        "status_title": profile["status_title"],
        "xp": profile["xp"],
        "credits_balance": profile["credits_balance"],
        "friends_invited": profile["friends_invited"],
        "tasks_completed": profile["tasks_completed"],
        "requests_total": profile["requests_total"],
    }
