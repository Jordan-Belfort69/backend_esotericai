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
    print(f"🔍 [auth_service] Получен initData (первые 100 символов): {init_data[:100]}...")

    # init_data уже такого вида: "query_id=...&user=...&auth_date=...&hash=..."
    params = dict(parse_qsl(init_data, keep_blank_values=True))

    hash_value = params.pop("hash", None)
    if not hash_value:
        raise ValueError("Missing hash parameter")

    sorted_params = sorted(params.items(), key=lambda x: x[0])
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_params)

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
        print("❌ [auth_service] Hash mismatch!")
        print(f"❌ [auth_service] Computed: {computed_hash}")
        print(f"❌ [auth_service] Expected: {hash_value}")
        print(f"❌ [auth_service] Data check string (first 200 chars): {data_check_string[:200]}")
        raise ValueError("Invalid signature")

    print("✅ [auth_service] Хеш валидирован успешно!")

    user_data_str = params.get("user")
    if not user_data_str:
        raise ValueError("Missing user parameter")

    user_data = json.loads(user_data_str)

    photo_url = user_data.get("photo_url") or f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data['id']}"

    print(
        f"✅ [auth_service] Пользователь: {user_data.get('first_name')} "
        f"(id={user_data.get('id')}, photo_url={photo_url})"
    )

    ensure_user_exists(
        user_id=user_data["id"],
        first_name=user_data["first_name"],
        username=user_data.get("username"),
        photo_url=photo_url,
    )

    return TelegramUser(
        user_id=user_data["id"],
        first_name=user_data["first_name"],
        last_name=user_data.get("last_name"),
        username=user_data.get("username"),
        language_code=user_data["language_code"],
        allows_write_to_pm=user_data.get("allows_write_to_pm", False),
        photo_url=photo_url,
    )


def ensure_user_exists(
    user_id: int,
    first_name: str,
    username: str | None = None,
    photo_url: str | None = None,
) -> None:
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (
                user_id, first_name, username, created_at, updated_at,
                messages_balance, photo_url
            ) VALUES (?, ?, ?, ?, ?, 0, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username   = excluded.username,
                updated_at = excluded.updated_at,
                photo_url  = excluded.photo_url
            """,
            (
                user_id,
                first_name,
                username,
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
                photo_url,
            ),
        )
        conn.commit()
    finally:
        conn.close()
