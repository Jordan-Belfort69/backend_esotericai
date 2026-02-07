# app/api/horoscope.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal
from app.deps.current_user import CurrentUserDep
from app.services.horoscope_service import create_horoscope_stub  # пока заглушка
from app.services.history_service import log_event

router = APIRouter(prefix="/api")

class HoroscopeRequest(BaseModel):
    zodiac: str
    scope: Literal["none", "career", "money", "love", "health"]

@router.post("/horoscope")
async def get_horoscope(
    request: HoroscopeRequest,
    user_id: CurrentUserDep,
):
    text = create_horoscope_stub(zodiac=request.zodiac, scope=request.scope)

    log_event(
        user_id=user_id,
        event_type="horoscope",                     # ключ для истории
        question=f"{request.zodiac}/{request.scope}",
        answer_full=text,
    )

    return {"text": text}
