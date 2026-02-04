# ===== ИСПРАВЛЕННЫЙ КОД =====
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = PROJECT_ROOT / "app"
DB_PATH = BASE_DIR / "db" / "users.db"
BOT_TOKEN = "8585375528:AAHlPi5dhKHwU5b7AEqf_Y6Ogy7zIygWc5Q"

# ✅ ИСПРАВЛЕНО: Убраны пробелы в ключах!
LEVELS = [
    {"code": "spark", "title": "Искра", "min_xp": 0, "max_xp": 99},
    {"code": "seeker", "title": "Ищущая", "min_xp": 100, "max_xp": 299},
    {"code": "initiated", "title": "Посвящённая", "min_xp": 300, "max_xp": 699},
    {"code": "keeper", "title": "Хранительница карт", "min_xp": 700, "max_xp": 1199},
    {"code": "moon_priestess", "title": "Лунная Жрица", "min_xp": 1200, "max_xp": 1999},
    {"code": "circle_leader", "title": "Ведущая кругов", "min_xp": 2000, "max_xp": 2999},
    {"code": "high_mystery", "title": "Верховная Мистерия", "min_xp": 3000, "max_xp": None},
]