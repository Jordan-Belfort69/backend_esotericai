# app/services/credits_service.py
from typing import Optional
from app.services.user_service import get_user_profile
from app.services.user_service import _get_user_row
from app.services.user_service import _get_connection

def get_balance(user_id: int) -> int:
    """
    Возвращает текущий баланс сообщений.
    """
    profile = get_user_profile(user_id)
    return profile.get("credits_balance", 0) if profile else 0

def add(user_id: int, amount: int) -> None:
    """
    Добавляет сообщения пользователю.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users 
            SET messages_balance = messages_balance + ?
            WHERE user_id = ?
        """, (amount, user_id))
        conn.commit()
    finally:
        conn.close()

def deduct(user_id: int, amount: int) -> bool:
    """
    Списывает сообщения у пользователя.
    Возвращает True, если успешно.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT messages_balance FROM users WHERE user_id = ?
        """, (user_id,))
        row = cur.fetchone()
        
        if not row or row[0] < amount:
            return False
            
        cur.execute("""
            UPDATE users 
            SET messages_balance = messages_balance - ?
            WHERE user_id = ?
        """, (amount, user_id))
        conn.commit()
        return True
    finally:
        conn.close()