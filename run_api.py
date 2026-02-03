import os
import uvicorn

if __name__ == "__main__":  # ← ИСПРАВЛЕНО: __name__ вместо name
    # Используем порт из переменной окружения
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)