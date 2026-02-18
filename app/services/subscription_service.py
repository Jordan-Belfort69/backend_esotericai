# app/services/subscription_service.py

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select

from core.config import CHANNEL_ID, GROUP_ID  # ← ИСПРАВЛЕНО
from app.services.tasks_service import increment_task_progress
from app.db.postgres import AsyncSessionLocal
from app.db.models import UserTask


async def is_task_completed(user_id: int, task_code: str) -> bool:
    """Проверяет, выполнено ли задание (reward_claimed = True)"""
    async with AsyncSessionLocal() as session:
        stmt = select(UserTask.reward_claimed).where(
            UserTask.user_id == user_id,
            UserTask.task_code == task_code
        )
        result = await session.execute(stmt)
        row = result.first()
        return bool(row[0]) if row else False


async def check_channel_subscription(bot: Bot, user_id: int) -> bool:
    """Проверяет подписку на канал"""
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except (TelegramBadRequest, Exception):
        return False


async def check_group_participation(bot: Bot, user_id: int) -> bool:
    """
    Проверяет подписку на группу.
    
    Примечание: Bot API не позволяет искать конкретные сообщения пользователя.
    Для отслеживания реальных отзывов используй handler в боте (см. ниже).
    Здесь проверяем только членство в группе.
    """
    try:
        member = await bot.get_chat_member(GROUP_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except (TelegramBadRequest, Exception):
        return False


async def check_and_complete_subscriptions(bot: Bot, user_id: int) -> None:
    """
    Автоматически проверяет подписки при запуске мини-аппа.
    Проверка происходит только если задание ещё не выполнено.
    """
    
    # D_1: подписка на канал
    if not await is_task_completed(user_id, "D_1"):
        if await check_channel_subscription(bot, user_id):
            await increment_task_progress(user_id, "D_1", delta=1)
    
    # D_2: подписка на группу (отзыв проверяется через handler)
    if not await is_task_completed(user_id, "D_2"):
        if await check_group_participation(bot, user_id):
            # Только членство не засчитываем, ждём реального сообщения
            pass
