# generate_initdata.py
import hmac
import hashlib
import urllib.parse
import json
from datetime import datetime, timezone

# Замени на свой реальный токен бота из core/config.py
BOT_TOKEN = "8585375528:AAHlPi5dhKHwU5b7AEqf_Y6Ogy7zIygWc5Q"  # ← ЗАМЕНИ НА СВОЙ ТОКЕН

def generate_init_data(user_id: int, first_name: str, username: str = None):
    user_data = {
        "id": user_id,
        "first_name": first_name,
        "last_name": "",
        "username": username or "",
        "language_code": "ru",
        "allows_write_to_pm": True
    }
    
    auth_date = int(datetime.now(timezone.utc).timestamp())
    
    params = {
        "user": json.dumps(user_data),
        "auth_date": str(auth_date),
    }
    
    # Сортируем и создаём строку для хеширования
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    
    # Генерируем секретный ключ
    secret_key = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    
    # Генерируем хеш
    hash_value = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    
    params["hash"] = hash_value
    
    # Кодируем в URL
    init_data = urllib.parse.urlencode(params)
    return init_data

# Генерируем для тестового пользователя
test_user_id = 123456789
test_first_name = "TestUser"
test_username = "testuser"

init_data = generate_init_data(test_user_id, test_first_name, test_username)
print("=" * 60)
print("СГЕНЕРИРОВАННЫЙ initData:")
print("=" * 60)
print(init_data)
print("=" * 60)
print(f"\nПолный URL для /api/me:\nhttp://localhost:8000/api/me?{init_data}")