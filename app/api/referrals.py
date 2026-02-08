# app/api/referrals.py

from fastapi import APIRouter, Depends
from app.deps.current_user import CurrentUserDep
from app.services.referrals_service import get_referrals_info

router = APIRouter(prefix="/api")

@router.get("/referrals/info")
def referrals_info(user_id: CurrentUserDep):
    """
    Возвращает реферальную информацию по фронтовому контракту.
    """
    return get_referrals_info(user_id)