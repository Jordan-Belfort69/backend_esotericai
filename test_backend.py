# test_backend.py
import requests
import urllib.parse

# Ваш сгенерированный initData
init_data = "user=%7B%22id%22%3A+123456789%2C+%22first_name%22%3A+%22TestUser%22%2C+%22last_name%22%3A+%22%22%2C+%22username%22%3A+%22testuser%22%2C+%22language_code%22%3A+%22ru%22%2C+%22allows_write_to_pm%22%3A+true%7D&auth_date=1770129662&hash=c01d0d029992ecc117df7d0d95d74c7c4d93eae32498ae802f4eeaa4b8006d40"

# Отправляем запрос
response = requests.get(
    "http://localhost:8000/api/me",
    params={"initData": init_data}
)

print("=" * 70)
print("РЕЗУЛЬТАТ ЗАПРОСА:")
print("=" * 70)
print(f"Статус: {response.status_code}")
print(f"Ответ: {response.json()}")
print("=" * 70)