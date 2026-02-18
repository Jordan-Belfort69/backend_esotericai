# config.py

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = PROJECT_ROOT / "app"

BOT_TOKEN = "8320610566:AAE1RlYeD7bpLaWaoZ9ZilVurR8JxsuJ7kM"

# Совет дня: картинки (карты — в img/cards/, пост с 3 картами — в img/advice/)
IMG_DIR = BASE_DIR / "img"
CARDS_IMG_DIR = IMG_DIR / "cards"
ADVICE_POST_IMAGE = IMG_DIR / "advice" / "post.png"

# ========== ДОБАВЬ ЭТИ СТРОКИ ==========
# Подписки для заданий D_1 и D_2
CHANNEL_ID = "@news_esotericai"  # канал с новостями
GROUP_ID = -1003679972336         # группа с отзывами
# =======================================

LEVELS = [
    {"code": "spark", "title": "Искра", "min_xp": 0, "max_xp": 99},
    {"code": "seeker", "title": "Ищущая", "min_xp": 100, "max_xp": 299},
    {"code": "initiated", "title": "Посвящённая", "min_xp": 300, "max_xp": 699},
    {"code": "keeper", "title": "Хранительница карт", "min_xp": 700, "max_xp": 1199},
    {"code": "moon_priestess", "title": "Лунная Жрица", "min_xp": 1200, "max_xp": 1999},
    {"code": "circle_leader", "title": "Ведущая кругов", "min_xp": 2000, "max_xp": 2999},
    {"code": "high_mystery", "title": "Верховная Мистерия", "min_xp": 3000, "max_xp": None},
]
