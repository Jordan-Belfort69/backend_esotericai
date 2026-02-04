import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any
from core.config import DB_PATH, LEVELS

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_user_exists(user_id: int, first_name: str, username: str | None = None) -> None:
    """Создаёт пользователя, если его нет."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO users (
            user_id, first_name, username, created_at, updated_at,
            messages_balance
        ) VALUES (?, ?, ?, ?, ?, 0)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            updated_at = excluded.updated_at
        """, (
            user_id,
            first_name,
            username,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ))
        conn.commit()
    finally:
        conn.close()

def _get_user_row(user_id: int) -> Optional[Dict[str, Any]]:
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT user_id, username, first_name, created_at, updated_at,
               messages_balance, is_banned
        FROM users WHERE user_id = ?
        """, (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    user = _get_user_row(user_id)
    if user is None:
        return None
    
    created_at = user.get("created_at") or datetime.utcnow().isoformat()
    
    # Подсчитываем друзей
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE referrer_id = ?", (user_id,))
        friends_invited = int(cur.fetchone()["cnt"] or 0)
        
        cur.execute("SELECT COUNT(*) AS cnt FROM history WHERE user_id = ?", (user_id,))
        requests_total = int(cur.fetchone()["cnt"] or 0)
        
        cur.execute("SELECT COUNT(*) AS cnt FROM user_tasks WHERE user_id = ? AND reward_claimed = 1", (user_id,))
        tasks_completed = int(cur.fetchone()["cnt"] or 0)
        
        cur.execute("SELECT xp FROM user_xp WHERE user_id = ?", (user_id,))
        xp_row = cur.fetchone()
        xp = int(xp_row["xp"]) if xp_row and xp_row["xp"] is not None else 0
    finally:
        conn.close()
    
    # Определяем уровень
    current_level = LEVELS[0]
    for lvl in LEVELS:
        min_xp = lvl["min_xp"]
        max_xp = lvl["max_xp"]
        if max_xp is None:
            if xp >= min_xp:
                current_level = lvl
            break
        if min_xp <= xp <= max_xp:
            current_level = lvl
            break
    
    # Баланс: используем messages_balance
    balance = int(user.get("messages_balance") or 0)
    
    return {
        "name": user.get("first_name") or "",
        "username": user.get("username") or "",
        "registered_at": created_at,
        "status_code": current_level["code"],
        "status_title": current_level["title"],
        "credits_balance": balance,
        "friends_invited": friends_invited,
        "tasks_completed": tasks_completed,
        "requests_total": requests_total,
        "xp": xp,
    }