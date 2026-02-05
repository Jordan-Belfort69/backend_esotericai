import sqlite3
from core.config import DB_PATH

def main():
    print("DB_PATH =", DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Схема таблицы users
    cur.execute("PRAGMA table_info(users)")
    cols = cur.fetchall()
    print("🧩 users columns:")
    for c in cols:
        print(dict(c))

    # Последние пользователи
    cur.execute("""
        SELECT user_id, first_name, username, photo_url, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT 20
    """)
    rows = cur.fetchall()
    print(f"🔢 found {len(rows)} users")
    for r in rows:
        print(dict(r))

    conn.close()

if __name__ == "__main__":
    main()
