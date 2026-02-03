import uvicorn

if __name__ == "__main__":  # ← Важно: __name__ а не name
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)