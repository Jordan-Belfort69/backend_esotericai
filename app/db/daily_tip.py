# app/db/daily_tip.py

import sqlite3
from pathlib import Path
from datetime import datetime, timezone as dt_timezone
from core.config import DB_PATH


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_daily_tip_table() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_tip_settings (
            user_id INTEGER PRIMARY KEY,
            enabled INTEGER NOT NULL,
            time_from TEXT,
            time_to TEXT,
            timezone TEXT,
            updated_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS advice_sent_log (
            user_id INTEGER NOT NULL,
            sent_date TEXT NOT NULL,
            PRIMARY KEY (user_id, sent_date)
        )
        """
    )
    conn.commit()
    conn.close()


def was_advice_sent_today(user_id: int, date_str: str) -> bool:
    """Проверяет, отправляли ли уже совет дня этому пользователю в эту дату."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM advice_sent_log WHERE user_id = ? AND sent_date = ?",
            (user_id, date_str),
        )
        return cur.fetchone() is not None
    finally:
        conn.close()


def mark_advice_sent(user_id: int, date_str: str) -> None:
    """Отмечает, что совет дня отправлен пользователю в эту дату."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO advice_sent_log (user_id, sent_date) VALUES (?, ?)",
            (user_id, date_str),
        )
        conn.commit()
    finally:
        conn.close()


def get_users_enabled_for_advice() -> list[tuple[int, str, str | None, str | None, str | None]]:
    """Возвращает (user_id, first_name, time_from, time_to, timezone) для всех с включённым советом дня."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT s.user_id, COALESCE(u.first_name, 'Друг') AS first_name,
                   s.time_from, s.time_to, s.timezone
            FROM daily_tip_settings s
            LEFT JOIN users u ON u.user_id = s.user_id
            WHERE s.enabled = 1
            """
        )
        return [
            (row["user_id"], row["first_name"], row["time_from"], row["time_to"], row["timezone"])
            for row in cur.fetchall()
        ]
    finally:
        conn.close()


def upsert_daily_tip_settings_db(
    user_id: int,
    enabled: bool,
    time_from: str | None,
    time_to: str | None,
    tz: str | None,
) -> dict:
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now(dt_timezone.utc).isoformat()

    cur.execute(
        """
        INSERT INTO daily_tip_settings (user_id, enabled, time_from, time_to, timezone, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            enabled = excluded.enabled,
            time_from = excluded.time_from,
            time_to = excluded.time_to,
            timezone = excluded.timezone,
            updated_at = excluded.updated_at
        """,
        (user_id, int(enabled), time_from, time_to, tz, now),
    )
    conn.commit()

    cur.execute(
        "SELECT user_id, enabled, time_from, time_to, timezone, updated_at "
        "FROM daily_tip_settings WHERE user_id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()

    return {
        "user_id": row[0],
        "enabled": bool(row[1]),
        "time_from": row[2],
        "time_to": row[3],
        "timezone": row[4],
        "updated_at": row[5],
    }
