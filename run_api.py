# run_api.py
import os
import asyncio
import uvicorn

from app.main import app          # твое FastAPI‑приложение
from bot_main import start_bot    # только что добавленная функция


async def start_api():
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    # параллельный запуск API и бота в одном event loop
    await asyncio.gather(
        start_api(),
        start_bot(),
    )


if __name__ == "__main__":
    asyncio.run(main())
