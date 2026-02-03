import os
import uvicorn

if __name__ == "__main__":  # Добавьте двойные подчеркивания!
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "app.main:app",  # Правильный путь к файлу внутри папки app
        host="0.0.0.0", 
        port=port, 
        reload=False
    )