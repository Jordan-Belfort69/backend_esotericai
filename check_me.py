# check_me.py
import requests

init_data = "user=%7B%22id%22%3A+123456789%2C+%22first_name%22%3A+%22TestUser%22%2C+%22last_name%22%3A+%22%22%2C+%22username%22%3A+%22testuser%22%2C+%22language_code%22%3A+%22ru%22%2C+%22allows_write_to_pm%22%3A+true%7D&auth_date=1769704536&hash=26828877c6abfa2ddceedd7f27fecee9c2895c030276045a854fc5b0cc8451ce"

url = "http://localhost:8000/api/me"
params = {"initData": init_data}

try:
    response = requests.get(url, params=params, timeout=5)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text}")
except requests.exceptions.ConnectionError:
    print("❌ Ошибка: Сервер не запущен. Запусти: python run_api.py")
except Exception as e:
    print(f"❌ Ошибка: {e}")