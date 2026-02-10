# compare_sqlite_neon.py

import asyncio
import sqlite3
from pathlib import Path
from typing import Dict, Set

from sqlalchemy import select, func

from app.db.postgres import AsyncSessionLocal
from app.db import models as m


# Путь к старой SQLite БД
PROJECT_ROOT = Path(__file__).resolve().parent
SQLITE_DB_PATH = PROJECT_ROOT / "app" / "db" / "users.db"

TABLES = [
    "users",
    "user_xp",
    "user_tasks",
    "daily_tip_settings",
    "history",
    "levels",
    "promo_codes",
    "referral_links",
    "referrals",
    "sms_purchases",
    "user_promocodes",
]


def get_sqlite_counts() -> Dict[str, int | None]:
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    counts: Dict[str, int | None] = {}
    for name in TABLES:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (name,),
        )
        if not cur.fetchone():
            counts[name] = None
            continue
        cur.execute(f"SELECT COUNT(*) AS cnt FROM {name}")
        counts[name] = cur.fetchone()["cnt"]
    conn.close()
    return counts


async def get_postgres_counts() -> Dict[str, int]:
    counts: Dict[str, int] = {}
    async with AsyncSessionLocal() as session:
        model_map = {
            "users": m.User,
            "user_xp": m.UserXP,
            "user_tasks": m.UserTask,
            "daily_tip_settings": m.DailyTipSettings,
            "history": m.History,
            "levels": m.Level,
            "promo_codes": m.PromoCode,
            "referral_links": m.ReferralLink,
            "referrals": m.Referral,
            "sms_purchases": m.SmsPurchase,
            "user_promocodes": m.UserPromocode,
        }
        for name, model in model_map.items():
            res = await session.execute(
                select(func.count()).select_from(model)
            )
            counts[name] = res.scalar_one()
    return counts


def get_all_sqlite_user_ids() -> Set[int]:
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    ids = {int(row["user_id"]) for row in cur.fetchall()}
    conn.close()
    return ids


async def get_all_postgres_user_ids() -> Set[int]:
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(m.User.user_id))
        return {row[0] for row in res.fetchall()}


def get_all_sqlite_promo_codes() -> Set[str]:
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("SELECT code FROM promo_codes")
    except sqlite3.OperationalError:
        conn.close()
        return set()
    codes = {str(row["code"]).upper() for row in cur.fetchall()}
    conn.close()
    return codes


async def get_all_postgres_promo_codes() -> Set[str]:
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(m.PromoCode.code))
        return {row[0].upper() for row in res.fetchall() if row[0] is not None}


async def main():
    # 1) Сравнение количества строк
    sqlite_counts = get_sqlite_counts()
    pg_counts = await get_postgres_counts()

    print("=== ROW COUNTS COMPARISON ===")
    for name in TABLES:
        sc = sqlite_counts.get(name)
        pc = pg_counts.get(name)
        print(f"{name:18}  sqlite={sc}   postgres={pc}")

    # 2) Сравнение user_id
    print("\n=== USER_ID SET DIFF ===")
    sqlite_ids = get_all_sqlite_user_ids()
    pg_ids = await get_all_postgres_user_ids()
    only_sqlite = sqlite_ids - pg_ids
    only_pg = pg_ids - sqlite_ids
    print(f"Total in SQLite:  {len(sqlite_ids)}")
    print(f"Total in Postgres:{len(pg_ids)}")
    print(f"Only in SQLite:   {len(only_sqlite)}")
    print(f"Only in Postgres: {len(only_pg)}")
    if only_sqlite:
        print("  sample only in SQLite:", list(only_sqlite)[:10])
    if only_pg:
        print("  sample only in Postgres:", list(only_pg)[:10])

    # 3) Сравнение промокодов
    print("\n=== PROMO CODES SET DIFF ===")
    sqlite_codes = get_all_sqlite_promo_codes()
    pg_codes = await get_all_postgres_promo_codes()
    only_sqlite_p = sqlite_codes - pg_codes
    only_pg_p = pg_codes - sqlite_codes
    print(f"Total in SQLite:  {len(sqlite_codes)}")
    print(f"Total in Postgres:{len(pg_codes)}")
    print(f"Only in SQLite:   {len(only_sqlite_p)}")
    print(f"Only in Postgres: {len(only_pg_p)}")
    if only_sqlite_p:
        print("  sample only in SQLite:", list(only_sqlite_p)[:10])
    if only_pg_p:
        print("  sample only in Postgres:", list(only_pg_p)[:10])


if __name__ == "__main__":
    asyncio.run(main())
