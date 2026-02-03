# app/api/promocodes.py

from fastapi import APIRouter, Depends
from app.deps.current_user import CurrentUserDep
from app.services.promocodes_service import get_promocodes_for_user

router = APIRouter(prefix="/api")

@router.get("/promocodes/list")
def promocodes_list(user_id: CurrentUserDep):
    """
    Возвращает список активных промокодов пользователя в формате фронта.
    """
    promos = get_promocodes_for_user(user_id)
    return {
        "promocodes": promos
    }