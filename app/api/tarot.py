# app/api/tarot.py

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Literal

from app.deps.current_user import CurrentUserDep
from app.services.tarot_service import create_tarot_reading_stub
from app.services.history_service import log_event
from app.services.request_track_service import track_user_request

router = APIRouter(prefix="/api")


class TarotRequest(BaseModel):
    spread_type: Literal["one_card", "three_cards", "celtic_cross"] = "one_card"
    question: str = ""


@router.post("/tarot")
async def get_tarot(
    request: TarotRequest,
    user_id: CurrentUserDep,
):
    """
    Генерирует расклад Таро для пользователя (Mini App).
    """
    text = create_tarot_reading_stub(
        spread_type=request.spread_type,
        question=request.question,
    )

    await log_event(
        user_id=user_id,
        event_type="tarot",
        question=f"{request.spread_type}/{request.question}",
        answer_full=text,
    )

    # общий учёт запроса (daily + usage)
    await track_user_request(user_id, "tarot")

    return {"text": text}


@router.post("/tarot-bot")
async def get_tarot_bot(
    request: TarotRequest,
    http_request: Request,
):
    """
    Расклад Таро для обычного бота (user_id в query).
    """
    user_id_str = http_request.query_params.get("user_id")
    if not user_id_str:
        return {"detail": "user_id is required"}

    try:
        user_id = int(user_id_str)
    except ValueError:
        return {"detail": "user_id must be int"}

    text = create_tarot_reading_stub(
        spread_type=request.spread_type,
        question=request.question,
    )

    await log_event(
        user_id=user_id,
        event_type="tarot",
        question=f"{request.spread_type}/{request.question}",
        answer_full=text,
    )

    await track_user_request(user_id, "tarot_bot")

    return {"text": text}
