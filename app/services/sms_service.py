# app/services/sms_service.py

from typing import NamedTuple, Optional
from datetime import datetime, timezone as dt_timezone

from sqlalchemy import select

from app.db.postgres import AsyncSessionLocal
from app.db.models import PromoCode


class PreviewResult(NamedTuple):
    base_price_rub: int
    final_price_rub: int
    discount_percent: Optional[int]
    promocode: Optional[str]
    error: Optional[str] = None


async def preview_sms_purchase(
    user_id: int,
    messages: int,
    promo_code: Optional[str] = None,
) -> PreviewResult:
    """
    Рассчитывает стоимость покупки сообщений.
    """
    PRICES = {
        100: 290,
        200: 490,
        300: 690,
        500: 990,
        1000: 1490,
    }

    base_price = PRICES.get(messages)
    if not base_price:
        return PreviewResult(
            base_price_rub=0,
            final_price_rub=0,
            discount_percent=None,
            promocode=None,
            error="Invalid messages amount",
        )

    final_price = base_price
    discount_percent: Optional[int] = None
    promocode: Optional[str] = None

    if promo_code:
        async with AsyncSessionLocal() as session:
            now = datetime.now(dt_timezone.utc)
            stmt = (
                select(PromoCode.discount_percent)
                .where(
                    PromoCode.code == promo_code,
                    PromoCode.is_active.is_(True),
                    PromoCode.expires_at > now,
                )
                .limit(1)
            )
            result = await session.execute(stmt)
            row = result.first()

        if row:
            discount_percent = row[0]
            promocode = promo_code
            final_price = int(base_price * (100 - discount_percent) / 100)

    return PreviewResult(
        base_price_rub=base_price,
        final_price_rub=final_price,
        discount_percent=discount_percent,
        promocode=promocode,
        error=None,
    )
