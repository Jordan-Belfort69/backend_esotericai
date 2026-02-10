# auth_service.py

import hashlib
import hmac
from urllib.parse import parse_qsl
from typing import Optional, NamedTuple
from datetime import datetime
import json

from core.config import BOT_TOKEN
from app.services.user_service import ensure_user_exists  # импорт async-функции


class TelegramUser(NamedTuple):
    user_id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    language_code: str
    allows_write_to_pm: bool
    photo_url: Optional[str] = None


async def validate_init_data(init_data: str) -> TelegramUser:
    print(f"🔍 [auth_service] Получен initData (первые 100 символов): {init_data[:100]}...")

    # init_data вида: "query_id=...&user=...&auth_date=...&hash=..."
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

    photo_url = user_data.get("photo_url") or (
        f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data['id']}"
    )

    print(
        f"✅ [auth_service] Пользователь: {user_data.get('first_name')} "
        f"(id={user_data.get('id')}, photo_url={photo_url})"
    )

    # создаём / обновляем пользователя в Neon
    await ensure_user_exists(
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
