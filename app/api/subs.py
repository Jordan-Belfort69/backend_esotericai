# app/api/subs.py

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.deps.current_user import CurrentUserDep
from app.services.sms_service import preview_sms_purchase
from app.db.postgres import AsyncSessionLocal
from app.db.models import SmsPurchase

router = APIRouter(prefix="/api")


# === Входные модели ===
class SubsQuoteRequest(BaseModel):
    messages: int  # 100, 200, 300, 500, 1000
    method: str = "sbp"  # sbp / card / stars
    promo_code: Optional[str] = None


class SubsCreateInvoiceRequest(BaseModel):
    messages: int
    method: str = "sbp"
    email: Optional[str] = None
    promo_code: Optional[str] = None
    client_confirmed_amount: int  # фронт подтверждает итоговую сумму


# === Ответы ===
class SubsQuoteResponse(BaseModel):
    messages: int
    method: str
    base_amount: int  # в копейках (например, 290 = 2.90 RUB)
    discount_percent: Optional[int]
    final_amount: int
    currency: str = "RUB"
    promo_code_applied: bool
    promo_message: Optional[str] = None


class SubsCreateInvoiceResponse(BaseModel):
    invoice_id: int
    provider: str = "stub"  # позже: yookassa, crypto и т.д.
    telegram_payload: dict  # заглушка для WebApp


@router.post("/subs/quote", response_model=SubsQuoteResponse)
async def subs_quote(
    body: SubsQuoteRequest,
    user_id: CurrentUserDep,
):
    """
    Возвращает расчёт покупки по фронтовому контракту.
    """
    package_map = {100: 100, 200: 200, 300: 300, 500: 500, 1000: 1000}
    if body.messages not in package_map:
        raise HTTPException(status_code=400, detail="Invalid messages amount")

    preview = await preview_sms_purchase(user_id, body.messages, body.promo_code)

    if preview.error:
        raise HTTPException(status_code=400, detail=preview.error)

    return SubsQuoteResponse(
        messages=body.messages,
        method=body.method,
        base_amount=int(preview.base_price_rub * 100),
        final_amount=int(preview.final_price_rub * 100),
        discount_percent=preview.discount_percent,
        promo_code_applied=bool(preview.promocode),
        currency="RUB",
    )


@router.post("/subs/create-invoice", response_model=SubsCreateInvoiceResponse)
async def subs_create_invoice(
    body: SubsCreateInvoiceRequest,
    user_id: CurrentUserDep,
):
    """
    Создаёт запись о покупке (заглушка под реальный платёжный сервис).
    """
    preview = await preview_sms_purchase(user_id, body.messages, body.promo_code)
    if preview.error:
        raise HTTPException(status_code=400, detail=preview.error)

    if body.client_confirmed_amount != int(preview.final_price_rub * 100):
        raise HTTPException(status_code=400, detail="Amount mismatch")

    async with AsyncSessionLocal() as session:
        now = datetime.utcnow().isoformat()

        purchase = SmsPurchase(
            user_id=user_id,
            messages_count=body.messages,
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

    return SubsCreateInvoiceResponse(
        invoice_id=invoice_id,
        provider="stub",
        telegram_payload={
            "title": f"Покупка {body.messages} сообщений",
            "description": "EsotericAI — мистические практики и инсайты",
            "prices": [{"label": "RUB", "amount": body.client_confirmed_amount}],
            "payload": {"invoice_id": invoice_id},
        },
    )
