from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

from app.deps.current_user import CurrentUserDep
from app.services.tarot_service import create_tarot_reading_stub
from app.services.history_service import log_event
from app.services.request_track_service import track_user_request  # NEW

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
    Генерирует расклад Таро для пользователя.
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
