import sqlite3
from pathlib import Path
from typing import Optional
from core.config import DB_PATH

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_messages_balance(user_id: int) -> int:
    """Возвращает текущий баланс сообщений пользователя."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT messages_balance FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()

def change_messages_balance(user_id: int, delta: int) -> None:
    """Изменяет баланс сообщений пользователя на указанную величину."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users
            SET messages_balance = messages_balance + ?
            WHERE user_id = ?
        """, (delta, user_id))
        conn.commit()
    finally:
        conn.close()

def get_user_xp(user_id: int) -> int:
    """Возвращает текущий XP пользователя."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT xp FROM user_xp WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()

def add_user_xp(user_id: int, amount: int) -> None:
    """Добавляет указанный опыт пользователю."""
    if amount <= 0:
        return
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_xp (user_id, xp)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                xp = xp + excluded.xp
        """, (user_id, amount))
        conn.commit()
    finally:
        conn.close()