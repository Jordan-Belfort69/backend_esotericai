# sync_promocodes_to_db.py
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import sqlite3
from app.promo_pools.promo_pool_5 import PROMO_CODES as POOL_5
from app.promo_pools.promo_pool_10 import PROMO_CODES as POOL_10
from app.promo_pools.promo_pool_15 import PROMO_CODES as POOL_15
from app.promo_pools.promo_pool_20 import PROMO_CODES as POOL_20
from app.promo_pools.promo_pool_25 import PROMO_CODES as POOL_25
from app.promo_pools.promo_pool_30 import PROMO_CODES as POOL_30

# Путь к БД
DB_PATH = PROJECT_ROOT / "app" / "db" / "users.db"

# Маппинг: процент → список кодов
POOLS = {
    5: POOL_5,
    10: POOL_10,
    15: POOL_15,
    20: POOL_20,
    25: POOL_25,
    30: POOL_30,
}

def sync_promocodes():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Создаём таблицу, если не существует
    cur.execute("""
        CREATE TABLE IF NOT EXISTS promocodes (
            code TEXT PRIMARY KEY,
            discount_percent INTEGER NOT NULL,
            expires_at DATETIME NOT NULL DEFAULT '2099-12-31 23:59:59',
            is_active BOOLEAN DEFAULT 1,
            description TEXT
        )
    """)

    total_inserted = 0

    for percent, codes in POOLS.items():
        if not codes:
            continue
        print(f"Обрабатываю {len(codes)} кодов для скидки {percent}%...")
        for code in codes:
            if not code.strip():
                continue
            clean_code = code.strip().upper()
            cur.execute("""
                INSERT OR IGNORE INTO promocodes 
                (code, discount_percent, description)
                VALUES (?, ?, ?)
            """, (clean_code, percent, f"{percent}% скидка"))

            if cur.rowcount > 0:
                total_inserted += 1

    conn.commit()
    conn.close()
    print(f"\n✅ Успешно добавлено {total_inserted} новых промокодов в БД.")
    print("Повторные запуски безопасны — дубликаты игнорируются.")

if __name__ == "__main__":
    sync_promocodes()