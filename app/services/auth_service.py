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
    """Возвращает соединение с БД."""
    return sqlite3.connect(DB_PATH)

def validate_init_data(init_data: str) -> TelegramUser:
    """
    Валидирует initData от Telegram и возвращает данные пользователя.
    Поддерживает новый формат с параметром 'signature'.
    """
    # Парсим параметры
    params = urllib.parse.parse_qs(init_data)
    
    # Извлекаем hash (обязательный параметр)
    hash_value = params.get("hash", [None])[0]
    if not hash_value:
        raise ValueError("Missing hash parameter")

    # Формируем данные для проверки подписи
    # Берём все параметры, кроме hash и signature
    check_data = []
    for key in sorted(params.keys()):
        if key in ("hash", "signature"):
            continue
        # Для каждого ключа может быть несколько значений (массив)
        for value in params[key]:
            check_data.append(f"{key}={value}")

    # Склеиваем через \n
    data_check_string = "\n".join(check_data)

    # Генерируем секретный ключ
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=BOT_TOKEN.encode(),
        digestmod=hashlib.sha256
    ).digest()

    # Вычисляем хеш
    expected_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Сравниваем хеши
    if not hmac.compare_digest(expected_hash, hash_value):
        raise ValueError("Invalid hash signature")

    # Извлекаем данные пользователя
    user_data_str = params.get("user", [None])[0]
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