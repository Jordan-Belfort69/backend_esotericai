import sqlite3
from core.config import DB_PATH

print("DB_PATH:", DB_PATH)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== TABLES ===")
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [row["name"] for row in cur.fetchall()]
for name in tables:
    print("-", name)

print("\n=== SCHEMAS ===")
for name in tables:
    print(f"\n-- {name} --")
    cur.execute(f"PRAGMA table_info({name});")
    for row in cur.fetchall():
        print(f"{row['name']:20} {row['type']:15} NOT NULL={row['notnull']} PK={row['pk']}")
