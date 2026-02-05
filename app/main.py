import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.me import router as me_router
from app.api.history import router as history_router
from app.api.tasks import router as tasks_router
from app.api.referrals import router as referrals_router
from app.api.promocodes import router as promocodes_router
from app.api.subs import router as subs_router
from app.api.rituals import router as rituals_router
from app.api.horoscope import router as horoscope_router
from app.api.tarot import router as tarot_router
from app.api.debug_db import router as debug_db_router
from app.services.auth_service import validate_init_data

app = FastAPI(title="EsotericAI Backend v3")

# ✅ ИСПРАВЛЕНО: Полный список доменов для CORS
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

# Middleware для валидации Telegram initData
@app.middleware("http")
async def validate_telegram_init_data(request: Request, call_next):
    init_data = request.query_params.get("initData")
    
    if init_data:
        try:
            # ✅ ВАЛИДИРУЕМ initData и СОЗДАЁМ ПОЛЬЗОВАТЕЛЯ
            user = validate_init_data(init_data)
            request.state.user_id = user.user_id
        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"detail": f"Invalid initData: {str(e)}"}
            )
    
    response = await call_next(request)
    return response

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
app.include_router(debug_db_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}