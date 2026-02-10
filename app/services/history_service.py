# app/services/history_service.py

from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import InstrumentedAttribute

from app.db.postgres import AsyncSessionLocal
from app.db.models import History


async def log_event(
    user_id: int,
    event_type: str,
    question: str,
    answer_full: str,
    meta_json: Optional[Dict] = None,  # пока не используем, для совместимости
) -> int:
    """Записывает событие в историю."""
    async with AsyncSessionLocal() as session:
        answer_short = (
            answer_full[:100] + "..." if len(answer_full) > 100 else answer_full
        )

        item = History(
            user_id=user_id,
            type=event_type,
            question=question,
            answer_full=answer_full,
            answer_short=answer_short,
            created_at=datetime.utcnow().isoformat(),
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item.id


async def list_history(user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Возвращает список событий истории."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                History.id,
                History.type,
                History.question,
                History.answer_short,
                History.created_at,
            )
            .where(History.user_id == user_id)
            .order_by(History.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        rows = result.all()

    return [
        {
            "id": row.id,
            "type": row.type,
            "title": row.question or "Запрос",
            "preview": row.answer_short or "",
            "created_at": row.created_at,
        }
        for row in rows
    ]


async def get_history_detail(user_id: int, event_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает полную запись истории."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                History.id,
                History.type,
                History.question,
                History.answer_full,
                History.created_at,
            )
            .where(
                History.id == event_id,
                History.user_id == user_id,
            )
        )
        result = await session.execute(stmt)
        row = result.first()

    if not row:
        return None

    row = row[0] if isinstance(row, tuple) else row  # на всякий случай

    return {
        "id": row.id,
        "type": row.type,
        "created_at": row.created_at,
        "question": row.question,
        "answer_full": row.answer_full,
        "full_text": row.answer_full,
    }
