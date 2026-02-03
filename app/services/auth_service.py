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
    Валидирует initData от Telegram (совместимо с версией 6.9+)
    """
    # ПАРСИМ ВРУЧНУЮ, чтобы сохранить URL-кодирование
    params = {}
    for pair in init_data.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value

    # Извлекаем hash
    hash_value = params.pop("hash", None)
    if not hash_value:
        raise ValueError("Missing hash parameter")

    # Формируем строку для проверки (без декодирования!)
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_params])

    # Генерируем секретный ключ (ПРАВИЛЬНЫЙ АЛГОРИТМ)
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()

    # Вычисляем хеш
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Проверяем подпись
    if not hmac.compare_digest(computed_hash, hash_value):
        print(f"❌ Hash mismatch!")
        print(f"Computed: {computed_hash}")
        print(f"Expected: {hash_value}")
        print(f"Data: {data_check_string[:100]}...")
        raise ValueError("Invalid signature")

    # Парсим user (только здесь декодируем)
    user_data_str = params.get("user")
    if not user_data_str:
        raise ValueError("Missing user parameter")

    import json
    user_data = json.loads(urllib.parse.unquote(user_data_str))

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
    Создаёт пользователя, если его нет. Используется при первом входе через WebApp.
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