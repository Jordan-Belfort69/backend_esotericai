# app/services/promocodes_service.py

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone as dt_timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func

from app.db.postgres import AsyncSessionLocal
from app.db.models import PromoCode, UserPromocode


async def take_promocode_from_pool(discount_percent: int) -> Optional[str]:
    """
    Берёт первый доступный (не выданный) промокод со скидкой `discount_percent`.
    """
    async with AsyncSessionLocal() as session:
        # промокоды нужной скидки, активные и не истёкшие
        base_stmt = (
            select(PromoCode.code)
            .where(
                PromoCode.discount_percent == discount_percent,
                PromoCode.is_active.is_(True),
                PromoCode.expires_at > datetime.now(dt_timezone.utc),
            )
            .order_by(PromoCode.code)
        )

        result = await session.execute(base_stmt)
        codes = [row[0] for row in result.all()]
        if not codes:
            return None

        # найдём первый код, который ещё не встречается в user_promocodes
        for code in codes:
            stmt_used = select(func.count()).select_from(UserPromocode).where(
                UserPromocode.code == code
            )
            used_count = (await session.execute(stmt_used)).scalar_one()
            if used_count == 0:
                return code

        return None


async def get_promocodes_for_user(user_id: int) -> List[Dict[str, Any]]:
    """
    Возвращает список промокодов пользователя в формате для фронта.
    """
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                PromoCode.code,
                PromoCode.discount_percent,
                PromoCode.expires_at,
            )
            .join(UserPromocode, UserPromocode.code == PromoCode.code)
            .where(
                UserPromocode.user_id == user_id,
                PromoCode.is_active.is_(True),
                PromoCode.expires_at > datetime.now(dt_timezone.utc),
            )
            .order_by(UserPromocode.assigned_at.desc())
        )
        result = await session.execute(stmt)
        rows = result.all()

    return [
        {
            "code": r.code,
            "discount": r.discount_percent,
            "expires_at": r.expires_at.isoformat()
            if isinstance(r.expires_at, datetime)
            else r.expires_at,
        }
        for r in rows
    ]


async def assign_promocode(user_id: int, code: str, source: str) -> None:
    """
    Выдаёт промокод пользователю (idempotent, как INSERT OR IGNORE).
    """
    now = datetime.now(dt_timezone.utc).isoformat()

    async with AsyncSessionLocal() as session:
        stmt = pg_insert(UserPromocode).values(
            user_id=user_id,
            code=code,
            assigned_at=now,
            source=source,
        ).on_conflict_do_nothing(
            index_elements=[UserPromocode.user_id, UserPromocode.code]
        )

        await session.execute(stmt)
        await session.commit()
