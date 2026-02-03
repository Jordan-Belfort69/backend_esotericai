# app/services/rituals_service.py

import sqlite3
from pathlib import Path
from typing import Dict, Any
from core.config import DB_PATH

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_daily_tip_settings(user_id: int) -> Dict[str, Any]:
    """
    Возвращает настройки ежедневного совета для пользователя.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT enabled, time_from, time_to, timezone, updated_at
            FROM daily_tip_settings
            WHERE user_id = ?
        """, (user_id,))
        row = cur.fetchone()
        if row:
            return {
                "enabled": bool(row["enabled"]),
                "time_from": row["time_from"],
                "time_to": row["time_to"],
                "timezone": row["timezone"],
                "updated_at": row["updated_at"],
            }
        else:
            return {
                "enabled": False,
                "time_from": None,
                "time_to": None,
                "timezone": "Europe/Moscow",
                "updated_at": None,
            }
    finally:
        conn.close()

def upsert_daily_tip_settings(
    user_id: int,
    enabled: bool,
    time_from: str | None,
    time_to: str | None,
    tz: str | None,
) -> Dict[str, Any]:
    """
    Сохраняет или обновляет настройки ежедневного совета.
    """
    from datetime import datetime, timezone as dt_timezone
    conn = _get_connection()
    try:
        cur = conn.cursor()
        now = datetime.now(dt_timezone.utc).isoformat()

        cur.execute("""
            INSERT INTO daily_tip_settings (user_id, enabled, time_from, time_to, timezone, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                enabled = excluded.enabled,
                time_from = excluded.time_from,
                time_to = excluded.time_to,
                timezone = excluded.timezone,
                updated_at = excluded.updated_at
        """, (user_id, int(enabled), time_from, time_to, tz, now))
        conn.commit()

        cur.execute("""
            SELECT user_id, enabled, time_from, time_to, timezone, updated_at
            FROM daily_tip_settings WHERE user_id = ?
        """, (user_id,))
        row = cur.fetchone()
        return {
            "user_id": row[0],
            "enabled": bool(row[1]),
            "time_from": row[2],
            "time_to": row[3],
            "timezone": row[4],
            "updated_at": row[5],
        }
    finally:
        conn.close()