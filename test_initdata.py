import hmac
import hashlib
import urllib.parse

BOT_TOKEN = "7911314861:AAHYyrnQZ4lmMfrbAjBPC-VcDR6WkOfpkIk"

encoded_init_data = (
    "query_id%3DAAF5yAk-AAAAAHnICT7tWgOK%26user%3D%257B%2522id%2522%253A1040828537%252C%2522first_name%2522%253A%2522Jordan%2522%252C%2522last_name%2522%253A%2522Belfort%2522%252C%2522username%2522%253A%2522j_belfort69%2522%252C%2522language_code%2522%253A%2522ru%2522%252C%2522allows_write_to_pm%2522%253Atrue%252C%2522photo_url%2522%253A%2522https%253A%255C%252F%255C%252Ft.me%255C%252Fi%255C%252Fuserpic%255C%252F320%255C%252FqgFthvR8JAWYdR1HIEzdDlQqqlj2hMQKL4rzJk0zydg.svg%2522%257D%26auth_date%3D1770154801%26signature%3DKB8r_qWH2YaoXiFNZDiQ6Up-hDgIVv0o7w1bjipi1PexT_QoqrQUAyMBt-UleFJPHZOy3mPIgvRX8c6H8VVoAQ%26hash%3D8d0091fd9e6f834896fc5c1030a67048b8a3aed36fef26cdd013aaa12c67b9d1"
)

# 1) Декодируем, как делает браузер
init_data = urllib.parse.unquote(encoded_init_data)
print("DECODED init_data:", init_data)

# 2) Разбираем на пары
params = {}
for pair in init_data.split("&"):
    if "=" in pair:
        k, v = pair.split("=", 1)
        params[k] = v

print("params keys:", list(params.keys()))

hash_value = params.pop("hash")
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

print("data_check_string:\n", data_check_string)
print("computed_hash:", computed_hash)
print("expected_hash:", hash_value)
print("match:", computed_hash == hash_value)
