# app/api/rituals.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from app.deps.current_user import CurrentUserDep
from app.services.rituals_service import get_daily_tip_settings, upsert_daily_tip_settings

router = APIRouter(prefix="/api/rituals")

class DailyTipSettingsIn(BaseModel):
    enabled: bool
    time_from: Optional[str] = None
    time_to: Optional[str] = None
    timezone: Optional[str] = "Europe/Moscow"

class DailyTipSettingsOut(BaseModel):
    enabled: bool
    time_from: Optional[str]
    time_to: Optional[str]
    timezone: Optional[str]

@router.get("/daily-tip-settings", response_model=DailyTipSettingsOut)
def get_settings(user_id: CurrentUserDep):
    settings = get_daily_tip_settings(user_id)
    return DailyTipSettingsOut(**settings)

@router.post("/daily-tip-settings", response_model=DailyTipSettingsOut)
def save_settings(payload: DailyTipSettingsIn, user_id: CurrentUserDep):
    settings = upsert_daily_tip_settings(
        user_id=user_id,
        enabled=payload.enabled,
        time_from=payload.time_from,
        time_to=payload.time_to,
        tz=payload.timezone,
    )
    return DailyTipSettingsOut(**settings)

# === Dev-only endpoint (отключить в проде) ===
class DailyTipSettingsTestIn(BaseModel):
    user_id: int
    enabled: bool
    time_from: Optional[str] = None
    time_to: Optional[str] = None
    timezone: Optional[str] = "Europe/Moscow"

@router.post("/daily-tip-settings-test", response_model=DailyTipSettingsOut, include_in_schema=False)
def save_settings_test(payload: DailyTipSettingsTestIn):
    """
    Только для локального тестирования. Не отображается в OpenAPI.
    """
    settings = upsert_daily_tip_settings(
        user_id=payload.user_id,
        enabled=payload.enabled,
        time_from=payload.time_from,
        time_to=payload.time_to,
        tz=payload.timezone,
    )
    return DailyTipSettingsOut(**settings)