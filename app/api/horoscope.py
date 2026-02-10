from fastapi import APIRouter, Request
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
async def get_horoscope(
    request_body: HoroscopeRequest,
    user_id: CurrentUserDep,
):
    text = create_horoscope_stub(
        zodiac=request_body.zodiac,
        scope=request_body.scope,
    )

    await log_event(
        user_id=user_id,
        event_type="horoscope",
        question=f"{request_body.zodiac}/{request_body.scope}",
        answer_full=text,
    )

    return {"text": text}


@router.post("/horoscope-bot")
async def get_horoscope_bot(
    request_body: HoroscopeRequest,
    http_request: Request,
):
    user_id_str = http_request.query_params.get("user_id")
    if not user_id_str:
        return {"detail": "user_id is required"}

    try:
        user_id = int(user_id_str)
    except ValueError:
        return {"detail": "user_id must be int"}

    text = create_horoscope_stub(
        zodiac=request_body.zodiac,
        scope=request_body.scope,
    )

    await log_event(
        user_id=user_id,
        event_type="horoscope",
        question=f"{request_body.zodiac}/{request_body.scope}",
        answer_full=text,
    )

    return {"text": text}
