# app/api/history.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated
from app.deps.current_user import CurrentUserDep
from app.services.history_service import list_history, get_history_detail

router = APIRouter(prefix="/api")

@router.get("/history/list")
def history_list(
    user_id: CurrentUserDep,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    """
    Возвращает список записей истории пользователя.
    Соответствует фронтовому контракту.
    """
    items = list_history(user_id=user_id, limit=limit, offset=offset)
    return {
        "items": items
    }

@router.get("/history/detail/{record_id}")
def history_detail(
    record_id: int,
    user_id: CurrentUserDep,
):
    """
    Возвращает полную запись истории по ID.
    Проверяет, что запись принадлежит пользователю.
    """
    # В сервисе параметр называется event_id, а не record_id
    record = get_history_detail(user_id=user_id, event_id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="History record not found or access denied")
    return record