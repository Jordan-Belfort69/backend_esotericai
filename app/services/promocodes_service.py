# app/services/promocodes_service.py

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.config import DB_PATH

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def take_promocode_from_pool(discount_percent: int) -> Optional[str]:
    """
    Берёт первый доступный (не выданный) промокод со скидкой `discount_percent`.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT pc.code
            FROM promo_codes pc
            LEFT JOIN user_promocodes up ON pc.code = up.code
            WHERE pc.discount_percent = ?
              AND pc.is_active = 1
              AND up.code IS NULL
            ORDER BY pc.code
            LIMIT 1
        """, (discount_percent,))
        row = cur.fetchone()
        return row["code"] if row else None
    finally:
        conn.close()

def get_promocodes_for_user(user_id: int) -> List[Dict[str, Any]]:
    """
    Возвращает список промокодов пользователя в формате для фронта.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                pc.code,
                pc.discount_percent,
                pc.expires_at
            FROM user_promocodes up
            JOIN promo_codes pc ON pc.code = up.code
            WHERE up.user_id = ?
              AND pc.is_active = 1
              AND pc.expires_at > datetime('now')
            ORDER BY up.assigned_at DESC
        """, (user_id,))
        return [
            {
                "code": r["code"],
                "discount": r["discount_percent"],
                "expires_at": r["expires_at"],
            }
            for r in cur.fetchall()
        ]
    finally:
        conn.close()

def assign_promocode(user_id: int, code: str, source: str) -> None:
    """
    Выдаёт промокод пользователю.
    """
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO user_promocodes 
            (user_id, code, assigned_at, source)
            VALUES (?, ?, ?, ?)
        """, (user_id, code, now, source))
        conn.commit()
    finally:
        conn.close()