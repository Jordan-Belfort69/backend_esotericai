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

# CORS — временно максимально широкий, чтобы не мешал отладке
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # можно сузить позже до своего домена
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def validate_telegram_init_data(request: Request, call_next):
    # Пути, куда можно ходить без initData
    public_paths = {"/api/health", "/health"}

    # 1. Пропускаем preflight-запросы OPTIONS без проверки initData
    if request.method == "OPTIONS":
        return await call_next(request)

    # 2. Пропускаем публичные пути без проверки
    if request.url.path in public_paths:
        return await call_next(request)

    # 3. Сначала пробуем взять initData из query-параметров (GET-запросы и т.п.)
    init_data = request.query_params.get("initData")

    # 4. Если не нашли и это метод с телом — пробуем достать initData из JSON body
    if not init_data and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        try:
            body_bytes = await request.body()
            if body_bytes:
                import json

                body = json.loads(body_bytes.decode("utf-8"))
                init_data = body.get("initData")

                # Восстанавливаем request с тем же телом для дальнейших хэндлеров
                async def receive():
                    return {
                        "type": "http.request",
                        "body": body_bytes,
                        "more_body": False,
                    }

                request = Request(request.scope, receive)
        except Exception as e:
            print(f"⚠️ [middleware] failed to read body for initData: {e}")

    if not init_data:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    try:
        tg_user = validate_init_data(init_data)
    except Exception as e:
        print(f"❌ [middleware] initData validation failed: {e}")
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    # кладём user_id в state для CurrentUser
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
