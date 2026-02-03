# app/services/sms_service.py

import sqlite3
from pathlib import Path
from typing import NamedTuple, Optional
from core.config import DB_PATH

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class PreviewResult(NamedTuple):
    base_price_rub: int
    final_price_rub: int
    discount_percent: Optional[int]
    promocode: Optional[str]
    error: Optional[str] = None

def preview_sms_purchase(user_id: int, messages: int, promo_code: Optional[str] = None) -> PreviewResult:
    """
    Рассчитывает стоимость покупки сообщений.
    """
    # Базовые цены (можно вынести в конфиг)
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
            error="Invalid messages amount"
        )
    
    final_price = base_price
    discount_percent = None
    promocode = None
    
    # Применяем промокод (если указан и активен)
    if promo_code:
        conn = _get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT discount_percent
                FROM promocodes
                WHERE code = ? AND is_active = 1 AND expires_at > datetime('now')
            """, (promo_code,))
            row = cur.fetchone()
            if row:
                discount_percent = row["discount_percent"]
                promocode = promo_code
                final_price = int(base_price * (100 - discount_percent) / 100)
        finally:
            conn.close()
    
    return PreviewResult(
        base_price_rub=base_price,
        final_price_rub=final_price,
        discount_percent=discount_percent,
        promocode=promocode,
        error=None
    )