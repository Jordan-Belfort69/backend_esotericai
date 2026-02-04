# ===== ИСПРАВЛЕННЫЙ И ФИНАЛЬНЫЙ КОД =====
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
    """
    Валидирует initData от Telegram Mini Apps (официальный алгоритм)
    ВАЖНО: Для формирования хеша используем ИСХОДНЫЕ ЗАКОДИРОВАННЫЕ значения!
    """
    # ✅ ПАРСИМ ВРУЧНУЮ, чтобы сохранить закодированные значения для хеша
    params = {}
    for pair in init_data.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value  # value остаётся ЗАКОДИРОВАННЫМ!
    
    # ✅ ДЕБАЖНЫЙ ВЫВОД для отладки
    print(f"🔍 [auth_service] Получен initData (первые 100 символов): {init_data[:100]}...")
    print(f"🔍 [auth_service] Параметры: {list(params.keys())}")
    
    # ✅ Ищем хеш (только для Mini Apps)
    hash_value = params.pop("hash", None)
    if not hash_value:
        # Для совместимости с разными источниками (не обязательно)
        hash_value = params.pop("signature", None)
        if not hash_value:
            raise ValueError("Missing hash parameter")
    
    print(f"🔍 [auth_service] Hash из запроса: {hash_value[:20]}...")
    
    # ✅ Формируем строку из ЗАКОДИРОВАННЫХ значений (как требует Telegram)
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_params])
    
    # ✅ Вычисляем секретный ключ
    secret_key = hmac.new(
        key=b"WebAppData",  # ← Без пробела!
        msg=BOT_TOKEN.encode(),
        digestmod=hashlib.sha256,
    ).digest()
    
    # ✅ Вычисляем хеш
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    
    # ✅ Сравниваем хеши
    if not hmac.compare_digest(computed_hash, hash_value):
        print(f"❌ [auth_service] Hash mismatch!")
        print(f"❌ [auth_service] Computed: {computed_hash}")
        print(f"❌ [auth_service] Expected: {hash_value}")
        print(f"❌ [auth_service] Data check string (first 200 chars): {data_check_string[:200]}")
        raise ValueError("Invalid signature")
    
    print(f"✅ [auth_service] Хеш валидирован успешно!")
    
    # ✅ Теперь декодируем ТОЛЬКО параметр user для получения данных
    user_data_str = params.get("user")
    if not user_data_str:
        raise ValueError("Missing user parameter")
    
    # Декодируем URL → получаем JSON-строку → парсим в объект
    import json
    user_data = json.loads(urllib.parse.unquote(user_data_str))
    
    print(f"✅ [auth_service] Пользователь: {user_data.get('first_name')} (id={user_data.get('id')})")
    
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
    """
    Создаёт пользователя в БД, если его нет.
    """
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