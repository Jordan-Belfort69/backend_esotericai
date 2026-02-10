# app/services/payments_service.py

from typing import Optional
from datetime import datetime, timezone as dt_timezone

from app.services.sms_service import preview_sms_purchase
from app.services.user_service import ensure_user_exists
from app.services.credits_service import add
from app.db.postgres import AsyncSessionLocal
from app.db.models import SmsPurchase
from sqlalchemy import select


async def quote(
    user_id: int,
    messages: int,
    method: str,
    promo_code: Optional[str] = None,
) -> dict:
    """
    Рассчитывает стоимость покупки.
    """
    await ensure_user_exists(user_id, "Unknown", None)
    preview = await preview_sms_purchase(user_id, messages, promo_code)

    return {
        "base_amount": preview.base_price_rub,
        "final_amount": preview.final_price_rub,
        "discount_percent": preview.discount_percent,
        "promo_code_applied": bool(preview.promocode),
        "promo_message": f"Скидка {preview.discount_percent}%" if preview.discount_percent else None,
    }


async def create_invoice(
    user_id: int,
    messages: int,
    method: str,
    email: Optional[str] = None,
    promo_code: Optional[str] = None,
    client_confirmed_amount: int = 0,
) -> dict:
    """
    Создаёт счёт на оплату.
    """
    await ensure_user_exists(user_id, "Unknown", None)
    preview = await preview_sms_purchase(user_id, messages, promo_code)

    if int(preview.final_price_rub * 100) != client_confirmed_amount:
        raise ValueError("Amount mismatch")

    async with AsyncSessionLocal() as session:
        now = datetime.now(dt_timezone.utc).isoformat()

        purchase = SmsPurchase(
            user_id=user_id,
            messages_count=messages,
            base_price_rub=preview.base_price_rub,
            final_price_rub=preview.final_price_rub,
            promocode=preview.promocode,
            discount_percent=preview.discount_percent,
            status="pending",
            created_at=now,
            paid_at=None,
        )
        session.add(purchase)
        await session.commit()
        await session.refresh(purchase)

        invoice_id = purchase.id

    return {
        "invoice_id": invoice_id,
        "provider": "stub",
        "telegram_payload": {
            "title": f"Покупка {messages} сообщений",
            "description": "EsotericAI — мистические практики и инсайты",
            "prices": [{"label": "RUB", "amount": client_confirmed_amount}],
            "payload": {"invoice_id": invoice_id},
        },
    }


async def mark_paid(payment_id: int) -> None:
    """
    Помечает платёж как оплаченный и начисляет сообщения.
    """
    async with AsyncSessionLocal() as session:
        stmt = select(SmsPurchase).where(SmsPurchase.id == payment_id)
        result = await session.scalars(stmt)
        purchase = result.first()

        if not purchase:
            return

        await add(purchase.user_id, purchase.messages_count)

        purchase.status = "paid"
        purchase.paid_at = datetime.now(dt_timezone.utc).isoformat()

        await session.commit()
