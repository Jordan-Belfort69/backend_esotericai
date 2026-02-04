# ===== ИСПРАВЛЕННЫЙ КОД =====
import hashlib
import hmac
import urllib.parse
from typing import Optional, NamedTuple
import sqlite3
from datetime import datetime
from core.config import BOT_TOKEN, DB_PATH

class TelegramUser(NamedTuple):
    user_id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    language_code: str
    allows_write_to_pm: bool
    photo_url: Optional[str] = None

def _get_connection():
    return sqlite3.connect(DB_PATH)

def validate_init_data(init_data: str) -> TelegramUser:
    print(f"🔍 [BACKEND] Получен initData (первые 100 символов): {init_data[:100]}...")
    print(f"🔍 [BACKEND] Длина initData: {len(init_data)}")
    
    params = {}
    for pair in init_data.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value
    
    # ✅ ПРОВЕРЯЕМ ОБА ВАРИАНТА:
    hash_value = params.pop("hash", None)
    
    # Если нет "hash" - пробуем "signature" (Login Widget)
    if not hash_value:
        hash_value = params.pop("signature", None)
        if not hash_value:
            raise ValueError("Missing hash/signature parameter")
    
    # ✅ ОСТАЛЬНОЙ КОД БЕЗ ИЗМЕНЕНИЙ...
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_params])
    
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=BOT_TOKEN.encode(),
        digestmod=hashlib.sha256,
    ).digest()
    
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    
    if not hmac.compare_digest(computed_hash, hash_value):
        print(f"❌ Hash mismatch!")
        print(f"Computed: {computed_hash}")
        print(f"Expected: {hash_value}")
        print(f"Data: {data_check_string[:200]}...")
        raise ValueError("Invalid signature")

    # ✅ ИСПРАВЛЕНО: Убран пробел!
    user_data_str = params.get("user")
    if not user_data_str:
        raise ValueError("Missing user parameter")

    import json
    user_data = json.loads(urllib.parse.unquote(user_data_str))

    # ✅ ИСПРАВЛЕНО: Убраны пробелы в ключах!
    return TelegramUser(
        user_id=user_data["id"],
        first_name=user_data["first_name"],
        last_name=user_data.get("last_name"),
        username=user_data.get("username"),
        language_code=user_data["language_code"],
        allows_write_to_pm=user_data.get("allows_write_to_pm", False),
        photo_url=user_data.get("photo_url")
    )

def ensure_user_exists(user_id: int, first_name: str, username: str | None = None) -> None:
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO users (
            user_id, first_name, username, created_at, updated_at,
            messages_balance
        ) VALUES (?, ?, ?, ?, ?, 0)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            updated_at = excluded.updated_at
        """, (
            user_id,
            first_name,
            username,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ))
        conn.commit()
    finally:
        conn.close()