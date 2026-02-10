import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.me import router as me_router
from app.api.history import router as history_router
from app.api.tasks import router as tasks_router
from app.api.referrals import router as referrals_router
from app.api.promocodes import router as promocodes_router
from app.api.subs import router as subs_router
from app.api.rituals import router as rituals_router
from app.api.horoscope import router as horoscope_router
from app.api.tarot import router as tarot_router
from app.services.auth_service import validate_init_data


app = FastAPI(title="EsotericAI Backend v3")


# CORS — максимально широкий для отладки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def validate_telegram_init_data(request: Request, call_next):
    public_paths = {
        "/health",
        "/api/health",
        "/api/horoscope-bot",  # бот ходит сюда без initData
        "/api/tarot-bot",      # задел под будущее, если понадобится
    }

    # Пропускаем preflight OPTIONS
    if request.method == "OPTIONS":
        return await call_next(request)

    # Пропускаем публичные пути
    if request.url.path in public_paths:
        return await call_next(request)

    # Берём initData только из query
    init_data = request.query_params.get("initData")

    if not init_data:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    try:
        tg_user = await validate_init_data(init_data)
    except Exception as e:
        print(f"❌ [middleware] initData validation failed: {e}")
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    request.state.user_id = tg_user.user_id
    return await call_next(request)


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
