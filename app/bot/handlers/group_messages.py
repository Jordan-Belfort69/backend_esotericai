# app/bot/handlers/group_messages.py

from aiogram import Router, F
from aiogram.types import Message

from app.services.tasks_service import increment_task_progress
from app.config import GROUP_ID

router = Router()


@router.message(F.chat.id == GROUP_ID, F.text)
async def on_group_review(message: Message):
    """
    Отслеживает сообщения (отзывы) в группе.
    Когда пользователь пишет в группу — автоматически выполняется D_2.
    """
    user_id = message.from_user.id
    
    # Засчитываем задание D_2 при первом сообщении
    await increment_task_progress(user_id, "D_2", delta=1)
