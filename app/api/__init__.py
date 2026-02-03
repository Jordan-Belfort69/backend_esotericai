# app/api/__init__.py

from fastapi import APIRouter

from .me import router as me_router
from .history import router as history_router
from .tasks import router as tasks_router
from .referrals import router as referrals_router
from .promocodes import router as promocodes_router
from .subs import router as subs_router
from .rituals import router as rituals_router
from .horoscope import router as horoscope_router

api_router = APIRouter()

api_router.include_router(me_router)
api_router.include_router(history_router)
api_router.include_router(tasks_router)
api_router.include_router(referrals_router)
api_router.include_router(promocodes_router)
api_router.include_router(subs_router)
api_router.include_router(rituals_router)
api_router.include_router(horoscope_router)

# Экспортируем для совместимости с main.py
rituals = rituals_router
horoscope = horoscope_router