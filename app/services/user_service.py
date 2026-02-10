# user_service.py

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import select, func

from core.config import LEVELS
from app.db.postgres import AsyncSessionLocal
from app.db.models import User, History, UserTask, UserXP


async def ensure_user_exists(
    user_id: int,
    first_name: str,
    username: str | None = None,
    photo_url: str | None = None,
) -> None:
    """Создаёт пользователя, если его нет, или обновляет данные, если есть."""
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.scalars(stmt)
        user = result.first()

        now_str = datetime.utcnow().isoformat()

        if user is None:
            user = User(
                user_id=user_id,
                first_name=first_name,
                username=username,
                created_at=now_str,
                updated_at=now_str,
                messages_balance=0,
                photo_url=photo_url,
            )
            session.add(user)
        else:
            user.username = username
            user.updated_at = now_str
            user.photo_url = photo_url

        await session.commit()


async def _get_user_row(user_id: int) -> Optional[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        stmt = select(
            User.user_id,
            User.username,
            User.first_name,
            User.created_at,
            User.updated_at,
            User.messages_balance,
            User.is_banned,
            User.photo_url,
        ).where(User.user_id == user_id)

        result = await session.execute(stmt)
        row = result.mappings().first()
        return dict(row) if row else None


async def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    user = await _get_user_row(user_id)
    if user is None:
        return None

    created_at = user.get("created_at") or datetime.utcnow().isoformat()

    async with AsyncSessionLocal() as session:
        # друзья
        friends_cnt_stmt = (
            select(func.count())
            .select_from(User)
            .where(User.referrer_id == user_id)
        )
        friends_invited = (await session.execute(friends_cnt_stmt)).scalar_one() or 0

        # запросы
        requests_cnt_stmt = (
            select(func.count())
            .select_from(History)
            .where(History.user_id == user_id)
        )
        requests_total = (await session.execute(requests_cnt_stmt)).scalar_one() or 0

        # выполненные задания
        tasks_cnt_stmt = (
            select(func.count())
            .select_from(UserTask)
            .where(
                UserTask.user_id == user_id,
                UserTask.reward_claimed.is_(True),
            )
        )
        tasks_completed = (await session.execute(tasks_cnt_stmt)).scalar_one() or 0

        # XP
        xp_stmt = select(UserXP.xp).where(UserXP.user_id == user_id)
        xp_row = (await session.execute(xp_stmt)).first()
        xp = int(xp_row[0]) if xp_row and xp_row[0] is not None else 0

    # уровень
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

    balance = int(user.get("messages_balance") or 0)

    return {
        "name": user.get("first_name") or "",
        "username": user.get("username") or "",
        "photo_url": user.get("photo_url"),
        "registered_at": created_at,
        "status_code": (current_level.get("code") or "").strip(),
        "status_title": (current_level.get("title") or "").strip(),
        "credits_balance": balance,
        "friends_invited": friends_invited,
        "tasks_completed": tasks_completed,
        "requests_total": requests_total,
        "xp": xp,
    }
