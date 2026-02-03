import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))  # __file__ вместо file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Роутеры
from app.api.me import router as me_router
from app.api.history import router as history_router
from app.api.tasks import router as tasks_router
from app.api.referrals import router as referrals_router
from app.api.promocodes import router as promocodes_router
from app.api.subs import router as subs_router
from app.api.rituals import router as rituals_router
from app.api.horoscope import router as horoscope_router
from app.api.tarot import router as tarot_router

app = FastAPI(title="EsotericAI Backend v3")

# ✅ CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jordan-belfort69.github.io",
        "https://web-production-4d81b.up.railway.app",
        "https://web.telegram.org",
        "https://t.me"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(me_router)
app.include_router(history_router)
app.include_router(tasks_router)
app.include_router(referrals_router)
app.include_router(promocodes_router)
app.include_router(subs_router)
app.include_router(rituals_router)
app.include_router(horoscope_router)
app.include_router(tarot_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}