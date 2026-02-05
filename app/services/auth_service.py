import hashlib
import hmac
from urllib.parse import parse_qsl
from typing import Optional, NamedTuple
import sqlite3
from datetime import datetime
import json
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
    Валидация initData из Telegram Mini App
    """
    print(f"🔍 [auth_service] Получен initData (первые 100 символов): {init_data[:100]}...")
    
    params = dict(parse_qsl(init_data, keep_blank_values=True))
    
    # Извлекаем хеш и удаляем его из параметров
    hash_value = params.pop("hash", None)  # ✅ УБРАН ПРОБЕЛ!

    if not hash_value:
        raise ValueError("Missing hash parameter")

    print(f"🔍 [auth_service] Hash из запроса: {hash_value[:20]}...")
    print(f"🔍 [auth_service] Параметры после удаления hash: {list(params.keys())}")

    # Собираем данные для проверки (сортируем по ключам)
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_params])  # ✅ УБРАНЫ ПРОБЕЛЫ!

    # Генерируем секретный ключ
    secret_key = hmac.new(
        key=b"WebAppData",  # ✅ УБРАН ПРОБЕЛ!
        msg=BOT_TOKEN.encode(),
        digestmod=hashlib.sha256,
    ).digest()

    # Вычисляем хеш
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,  # ✅ ИСПРАВЛЕНО: diges tmod → digestmod
    ).hexdigest()

    # Сравниваем хеши
    if not hmac.compare_digest(computed_hash, hash_value):
        print(f"❌ [auth_service] Hash mismatch!")
        print(f"❌ [auth_service] Computed: {computed_hash}")
        print(f"❌ [auth_service] Expected: {hash_value}")
        print(f"❌ [auth_service] Data check string (first 200 chars): {data_check_string[:200]}")
        raise ValueError("Invalid signature")

    print(f"✅ [auth_service] Хеш валидирован успешно!")

    # Получаем данные пользователя
    user_data_str = params.get("user")  # ✅ УБРАН ПРОБЕЛ!
    if not user_data_str:
        raise ValueError("Missing user parameter")

    # Декодируем данные пользователя
    user_data = json.loads(user_data_str)

    # Генерируем URL аватарки, если photo_url отсутствует
    photo_url = None
    if "photo_url" in user_data and user_data["photo_url"]:  # ✅ УБРАНЫ ПРОБЕЛЫ!
        photo_url = user_data["photo_url"]
    else:
        # Используем Dicebear API для генерации аватарки
        photo_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data['id']}"

    print(f"✅ [auth_service] Пользователь: {user_data.get('first_name')} (id={user_data.get('id')}, photo_url={photo_url})")

    # Создаем пользователя в БД
    ensure_user_exists(
        user_id=user_data["id"],  # ✅ УБРАНЫ ПРОБЕЛЫ!
        first_name=user_data["first_name"],
        username=user_data.get("username"),
        photo_url=photo_url
    )

    return TelegramUser(
        user_id=user_data["id"],
        first_name=user_data["first_name"],
        last_name=user_data.get("last_name"),
        username=user_data.get("username"),
        language_code=user_data["language_code"],
        allows_write_to_pm=user_data.get("allows_write_to_pm", False),
        photo_url=photo_url
    )

def ensure_user_exists(user_id: int, first_name: str, username: str | None = None, photo_url: str | None = None) -> None:
    """
    Создаёт пользователя в БД, если его нет.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (
                user_id, first_name, username, created_at, updated_at,
                messages_balance, photo_url
            ) VALUES (?, ?, ?, ?, ?, 0, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                updated_at = excluded.updated_at,
                photo_url = excluded.photo_url
        """, (
            user_id,
            first_name,
            username,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat(),
            photo_url
        ))
        conn.commit()
    finally:
        conn.close()