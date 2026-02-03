# app/services/payments_service.py
from typing import Optional
from app.services.sms_service import preview_sms_purchase
from app.services.user_service import ensure_user_exists
from app.services.user_service import _get_connection

def quote(user_id: int, messages: int, method: str, promo_code: Optional[str] = None) -> dict:
    """
    Рассчитывает стоимость покупки.
    """
    ensure_user_exists(user_id, "Unknown", None)
    preview = preview_sms_purchase(user_id, messages, promo_code)
    
    return {
        "base_amount": preview.base_price_rub,
        "final_amount": preview.final_price_rub,
        "discount_percent": preview.discount_percent,
        "promo_code_applied": bool(preview.promocode),
        "promo_message": f"Скидка {preview.discount_percent}%" if preview.discount_percent else None,
    }

def create_invoice(
    user_id: int,
    messages: int,
    method: str,
    email: Optional[str] = None,
    promo_code: Optional[str] = None,
    client_confirmed_amount: int = 0
) -> dict:
    """
    Создаёт счёт на оплату.
    """
    ensure_user_exists(user_id, "Unknown", None)
    preview = preview_sms_purchase(user_id, messages, promo_code)
    
    if preview.final_price_rub * 100 != client_confirmed_amount:
        raise ValueError("Amount mismatch")
    
    conn = _get_connection()
    try:
        cur = conn.cursor()
        now = "2026-01-29T17:00:56"  # В реальности: datetime.utcnow().isoformat()
        cur.execute("""
            INSERT INTO sms_purchases (
                user_id, messages_count, base_price_rub, final_price_rub,
                promocode, discount_percent, status, created_at, paid_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, NULL)
        """, (
            user_id,
            messages,
            preview.base_price_rub,
            preview.final_price_rub,
            preview.promocode,
            preview.discount_percent,
            now,
        ))
        invoice_id = cur.lastrowid
        conn.commit()
    finally:
        conn.close()
    
    return {
        "invoice_id": invoice_id,
        "provider": "stub",
        "telegram_payload": {
            "title": f"Покупка {messages} сообщений",
            "description": "EsotericAI — мистические практики и инсайты",
            "prices": [{"label": "RUB", "amount": client_confirmed_amount}],
            "payload": {"invoice_id": invoice_id},
        }
    }

def mark_paid(payment_id: int) -> None:
    """
    Помечает платёж как оплаченный и начисляет сообщения.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, messages_count 
            FROM sms_purchases 
            WHERE id = ?
        """, (payment_id,))
        row = cur.fetchone()
        
        if not row:
            return
            
        user_id, messages = row
        # Начисляем сообщения
        from app.services.credits_service import add
        add(user_id, messages)
        
        # Обновляем статус платежа
        cur.execute("""
            UPDATE sms_purchases 
            SET status = 'paid', paid_at = datetime('now')
            WHERE id = ?
        """, (payment_id,))
        conn.commit()
    finally:
        conn.close()