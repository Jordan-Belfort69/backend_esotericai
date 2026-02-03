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
    conn.commit()
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
