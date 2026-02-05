import sqlite3
from core.config import DB_PATH  # если неудобно, можно заменить на прямой путь

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # подставь сюда свой user_id из логов (например, 1040828537)
    user_id = 1040828537

    cur.execute("""
        SELECT user_id, first_name, username, photo_url, created_at, updated_at
        FROM users
        WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()

    if not row:
        print(f"❌ Пользователь с user_id={user_id} не найден в БД")
    else:
        print("✅ Найден пользователь в БД:")
        for k in row.keys():
            print(f"  {k}: {row[k]}")

    conn.close()

if __name__ == "__main__":
    main()
