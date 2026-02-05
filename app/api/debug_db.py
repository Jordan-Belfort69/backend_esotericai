import sqlite3
from fastapi import APIRouter
from core.config import DB_PATH

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/users")
def debug_users():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Схема таблицы users
    cur.execute("PRAGMA table_info(users)")
    cols = [dict(r) for r in cur.fetchall()]

    # Последние пользователи
    cur.execute("""
        SELECT user_id, first_name, username, photo_url, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT 20
    """)
    users = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {
        "db_path": DB_PATH,
        "columns": cols,
        "users": users,
    }
