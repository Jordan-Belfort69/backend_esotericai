# final_test_all_endpoints.py
"""
ФИНАЛЬНЫЙ ТЕСТ ВСЕХ ЭНДПОИНТОВ
Проверяет соответствие фронтовому контракту
"""

import requests
import json

# Твой initData
INIT_DATA = "user=%7B%22id%22%3A+123456789%2C+%22first_name%22%3A+%22TestUser%22%2C+%22last_name%22%3A+%22%22%2C+%22username%22%3A+%22testuser%22%2C+%22language_code%22%3A+%22ru%22%2C+%22allows_write_to_pm%22%3A+true%7D&auth_date=1769704536&hash=26828877c6abfa2ddceedd7f27fecee9c2895c030276045a854fc5b0cc8451ce"

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, url, params=None, data=None, expected_fields=None):
    """Тестирует один эндпоинт."""
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, params=params, timeout=5)
        else:
            print(f"❌ {name:40} | НЕИЗВЕСТНЫЙ МЕТОД")
            return
        
        status = response.status_code
        result = "✅" if status == 200 else "⚠️" if status == 400 else "❌"
        
        # Проверяем структуру ответа
        try:
            json_data = response.json()
            has_fields = True
            if expected_fields:
                for field in expected_fields:
                    if field not in json_data:
                        has_fields = False
                        break
            
            fields_check = "✅" if has_fields else "❌"
        except:
            fields_check = "⚠️"
        
        print(f"{result} {name:40} | {method:4} | {status:3} | {fields_check} Структура")
        
        return {
            "name": name,
            "method": method,
            "status": status,
            "ok": status == 200,
            "fields_ok": has_fields if 'has_fields' in locals() else None
        }
        
    except Exception as e:
        print(f"❌ {name:40} | ERROR | {str(e)[:50]}")
        return {"name": name, "error": str(e)}

def run_all_tests():
    """Запускает все тесты."""
    print("=" * 100)
    print("🚀 ФИНАЛЬНЫЙ ТЕСТ ВСЕХ ЭНДПОИНТОВ")
    print("=" * 100)
    print()
    
    results = []
    
    # === 1. Проверка здоровья сервера ===
    print("🔧 БАЗОВЫЕ ЭНДПОИНТЫ")
    print("-" * 100)
    
    results.append(test_endpoint(
        "GET /health",
        "GET",
        f"{BASE_URL}/health"
    ))
    
    # === 2. Профиль пользователя ===
    print()
    print("👤 ПРОФИЛЬ И ПОЛЬЗОВАТЕЛЬ")
    print("-" * 100)
    
    results.append(test_endpoint(
        "GET /api/me",
        "GET",
        f"{BASE_URL}/api/me",
        params={"initData": INIT_DATA},
        expected_fields=["user_id", "name", "username", "status_code", "status_title", "xp", "credits_balance"]
    ))
    
    # === 3. История ===
    print()
    print("📚 ИСТОРИЯ")
    print("-" * 100)
    
    results.append(test_endpoint(
        "GET /api/history/list",
        "GET",
        f"{BASE_URL}/api/history/list",
        params={"initData": INIT_DATA},
        expected_fields=["items"]
    ))
    
    results.append(test_endpoint(
        "GET /api/history/detail/{id}",
        "GET",
        f"{BASE_URL}/api/history/detail/1",
        params={"initData": INIT_DATA},
        expected_fields=["id", "type", "created_at", "question", "answer_full"]
    ))
    
    # === 4. Задания ===
    print()
    print("🎯 ЗАДАНИЯ")
    print("-" * 100)
    
    results.append(test_endpoint(
        "GET /api/tasks/list (daily)",
        "GET",
        f"{BASE_URL}/api/tasks/list",
        params={"initData": INIT_DATA, "category": "daily"},
        expected_fields=["category", "tasks"]
    ))
    
    results.append(test_endpoint(
        "POST /api/tasks/claim",
        "POST",
        f"{BASE_URL}/api/tasks/claim",
        params={"initData": INIT_DATA},
        data={"task_code": "D_DAILY"}
    ))
    
    # === 5. Рефералка и промокоды ===
    print()
    print("🤝 РЕФЕРАЛКА И ПРОМОКОДЫ")
    print("-" * 100)
    
    results.append(test_endpoint(
        "GET /api/referrals/info",
        "GET",
        f"{BASE_URL}/api/referrals/info",
        params={"initData": INIT_DATA},
        expected_fields=["referral_link", "friends"]
    ))
    
    results.append(test_endpoint(
        "GET /api/promocodes/list",
        "GET",
        f"{BASE_URL}/api/promocodes/list",
        params={"initData": INIT_DATA},
        expected_fields=["promocodes"]
    ))
    
    # === 6. Покупки ===
    print()
    print("💳 ПОКУПКИ")
    print("-" * 100)
    
    results.append(test_endpoint(
        "POST /api/subs/quote",
        "POST",
        f"{BASE_URL}/api/subs/quote",
        params={"initData": INIT_DATA},
        data={"messages": 100, "method": "sbp"},
        expected_fields=["messages", "method", "base_amount", "final_amount", "currency"]
    ))
    
    results.append(test_endpoint(
        "POST /api/subs/create-invoice",
        "POST",
        f"{BASE_URL}/api/subs/create-invoice",
        params={"initData": INIT_DATA},
        data={
            "messages": 100,
            "method": "sbp",
            "email": None,
            "promo_code": None,
            "client_confirmed_amount": 29000
        },
        expected_fields=["invoice_id", "provider", "telegram_payload"]
    ))
    
    # === 7. Ритуалы и гороскоп ===
    print()
    print("🔮 РИТУАЛЫ И ГОРОСКОП")
    print("-" * 100)
    
    results.append(test_endpoint(
        "GET /api/rituals/daily-tip-settings",
        "GET",
        f"{BASE_URL}/api/rituals/daily-tip-settings",
        params={"initData": INIT_DATA},
        expected_fields=["enabled", "time_from", "time_to", "timezone"]
    ))
    
    results.append(test_endpoint(
        "POST /api/horoscope",
        "POST",
        f"{BASE_URL}/api/horoscope",
        params={"initData": INIT_DATA},
        data={"zodiac": "aries", "scope": "love"},
        expected_fields=["text"]
    ))
    
    # === 8. Таро ===
    print()
    print("🎴 ТАРО")
    print("-" * 100)
    
    results.append(test_endpoint(
        "POST /api/tarot",
        "POST",
        f"{BASE_URL}/api/tarot",
        params={"initData": INIT_DATA},
        data={"spread_type": "one_card", "question": "Что меня ждёт?"},
        expected_fields=["text"]
    ))
    
    # === ИТОГИ ===
    print()
    print("=" * 100)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 100)
    
    total = len(results)
    success = sum(1 for r in results if r.get("ok"))
    errors = sum(1 for r in results if r.get("error"))
    
    print(f"\n✅ Успешно: {success}/{total}")
    print(f"❌ Ошибки: {errors}/{total}")
    
    if errors > 0:
        print("\n⚠️  ЭНДПОИНТЫ С ОШИБКАМИ:")
        for r in results:
            if r.get("error"):
                print(f"   • {r['name']}: {r['error']}")
    
    print("\n" + "=" * 100)
    
    return results

if __name__ == "__main__":
    # Проверяем, запущен ли сервер
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ Сервер запущен и работает\n")
            run_all_tests()
        else:
            print("❌ Сервер не отвечает. Запусти: python run_api.py")
    except:
        print("❌ Сервер не запущен. Запусти: python run_api.py")