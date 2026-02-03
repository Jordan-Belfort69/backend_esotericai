# app/api/horoscope.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from app.deps.current_user import CurrentUserDep
from app.services.horoscope_service import create_horoscope_stub
from app.services.history_service import log_event

router = APIRouter(prefix="/api")

class HoroscopeRequest(BaseModel):
    zodiac: str
    scope: Literal["none", "career", "money", "love", "health"]

@router.post("/horoscope")
def get_horoscope(
    request: HoroscopeRequest,
    user_id: CurrentUserDep,
):
    """
    Генерирует гороскоп для пользователя.
    """
    # Генерируем текст гороскопа
    text = create_horoscope_stub(zodiac=request.zodiac, scope=request.scope)
    
    # Записываем в историю
    log_event(
        user_id=user_id,
        event_type="horoscope",
        question=f"{request.zodiac}/{request.scope}",
        answer_full=text
    )
    
    return {
        "text": text
    }