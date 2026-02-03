from fastapi import APIRouter, Depends, HTTPException, status
from app.deps.current_user import CurrentUserDep
from app.services.user_service import get_user_profile


router = APIRouter(prefix="/api")


@router.get("/me")
def get_me(user_id: CurrentUserDep):
    """
    Возвращает профиль пользователя с полным статусом.
    Структура ответа соответствует фронтовому контракту.
    """
    profile = get_user_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    # ✅ УБРАНЫ ПРОБЕЛЫ В КЛЮЧАХ!
    return {
        "user_id": user_id,
        "name": profile["name"],
        "username": profile["username"],
        "registered_at": profile["registered_at"],
        "status_code": profile["status_code"],
        "status_title": profile["status_title"],
        "xp": profile["xp"],
        "credits_balance": profile["credits_balance"],
        "friends_invited": profile["friends_invited"],
        "tasks_completed": profile["tasks_completed"],
        "requests_total": profile["requests_total"],
    }
