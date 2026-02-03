# app/services/referrals_service.py

import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from core.config import DB_PATH

# === НАСТРОЙКА: замени на имя твоего бота ===
BOT_USERNAME = "ai_esoterictestbot"  # ← Уже правильно!

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_ref_code() -> str:
    """Генерирует уникальный реферальный код"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_or_create_ref_code(user_id: int) -> str:
    """Получает или создаёт реферальный код для пользователя."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT ref_code FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        
        if row and row[0]:
            return row[0]
        
        # Генерируем новый реферальный код
        ref_code = generate_ref_code()
        cur.execute("""
            UPDATE users 
            SET ref_code = ?
            WHERE user_id = ?
        """, (ref_code, user_id))
        conn.commit()
        return ref_code
    finally:
        conn.close()

def get_referrals_info(user_id: int) -> Dict[str, Any]:
    """Возвращает данные для /api/referrals/info по фронтовому контракту."""
    ref_code = get_or_create_ref_code(user_id)
    referral_link = f"https://t.me/ai_esoterictestbot?start={ref_code}"

    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT first_name, username, created_at
            FROM users
            WHERE referrer_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cur.fetchall()
        friends = []
        for r in rows:
            name = r["first_name"] or r["username"] or "Друг"
            friends.append({
                "name": name,
                "joined_at": r["created_at"],
                "bonus_credits": 0,
                "status": "joined",
            })
        return {
            "referral_link": referral_link,
            "friends": friends,
        }
    finally:
        conn.close()