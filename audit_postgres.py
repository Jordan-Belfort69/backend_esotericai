import asyncio
from typing import Dict, List, Tuple

from sqlalchemy import select, func, text
from app.db.postgres import AsyncSessionLocal
from app.db import models as m


TABLE_MODELS = {
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
    # добавь сюда другие модели, если есть
}


UNIQUE_CHECKS = {
    "users": ["user_id"],
    "user_xp": ["user_id"],
    "user_tasks": ["user_id", "task_code"],        # составной PK
    "promo_codes": ["code"],                       # PK
    "referral_links": ["user_id"],                 # PK
    "referrals": ["id"],                           # PK
    "sms_purchases": ["id"],                       # PK
    "user_promocodes": ["user_id", "code"],        # составной PK + UniqueConstraint
}



async def check_row_counts(session) -> Dict[str, int]:
    print("=== ROW COUNTS ===")
    counts = {}
    for name, model in TABLE_MODELS.items():
        res = await session.execute(select(func.count()).select_from(model))
        cnt = res.scalar_one()
        counts[name] = cnt
        print(f"{name:18} -> {cnt}")
    print()
    return counts


async def check_duplicates(session) -> None:
    print("=== DUPLICATES CHECK ===")
    for table, cols in UNIQUE_CHECKS.items():
        model = TABLE_MODELS[table]
        # строим выражения колонок
        columns = [getattr(model, c) for c in cols]

        stmt = (
            select(*columns, func.count())
            .select_from(model)
            .group_by(*columns)
            .having(func.count() > 1)
        )
        res = await session.execute(stmt)
        rows = res.all()
        if rows:
            print(f"[!] Duplicates in {table} by {cols}:")
            for r in rows:
                print("   ", r)
        else:
            print(f"{table}: no duplicates by {cols}")
    print()


async def check_nulls_in_keys(session) -> None:
    print("=== NULLS IN KEY COLUMNS ===")
    for table, cols in UNIQUE_CHECKS.items():
        model = TABLE_MODELS[table]
        for col in cols:
            column = getattr(model, col)
            stmt = select(func.count()).select_from(model).where(column.is_(None))
            res = await session.execute(stmt)
            cnt = res.scalar_one()
            if cnt > 0:
                print(f"[!] {table}.{col} has {cnt} NULLs")
            else:
                print(f"{table}.{col}: OK (no NULLs)")
    print()


async def main():
    async with AsyncSessionLocal() as session:
        await check_row_counts(session)
        await check_duplicates(session)
        await check_nulls_in_keys(session)


if __name__ == "__main__":
    asyncio.run(main())
