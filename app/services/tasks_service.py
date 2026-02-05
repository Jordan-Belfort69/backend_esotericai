import sqlite3
from typing import List, Dict, Any
from core.config import DB_PATH
from app.services.user_balance_service import (
    change_messages_balance,
    add_user_xp,
)

# === КОНФИГ ЗАДАЧ (с текстами, как во фронте) ===
TASK_CONFIG: Dict[str, Dict[str, Any]] = {
    # Daily
    "D_DAILY": {
        "category": "daily",
        "progress_target": 1,
        "title": "Ежедневный вход",
        "desc": "Зайди в бота хотя бы один раз за день.",
    },
    "D_REQ_DAILY": {
        "category": "daily",
        "progress_target": 1,
        "title": "Ежедневный запрос",
        "desc": "Сделай минимум один запрос боту в течение дня.",
    },

    # Activity
    "D_1": {
        "category": "activity",
        "progress_target": 1,
        "title": "Подписка на канал",
        "desc": "Подпишись на новостной канал проекта, чтобы получать обновления и акции.",
    },
    "D_2": {
        "category": "activity",
        "progress_target": 1,
        "title": "Подписка и отзыв",
        "desc": "Подпишись на нашу группу с отзывами о проекте и оставь свой честный отзыв.",
    },
    "D_3": {
        "category": "activity",
        "progress_target": 7,
        "title": "Активность 7 дней",
        "desc": "Будь активна 7 дней подряд: минимум один запрос боту каждый день.",
    },
    "D_4": {
        "category": "activity",
        "progress_target": 14,
        "title": "Активность 14 дней",
        "desc": "Сохраняй активность 14 дней подряд — бот всегда под рукой.",
    },
    "D_5": {
        "category": "activity",
        "progress_target": 30,
        "title": "Активность 30 дней",
        "desc": "30 дней с практикой и подсказками от бота — мягкое, но устойчивое движение вперёд.",
    },

    # Referral
    "REF_1": {
        "category": "referral",
        "progress_target": 3,
        "title": "Пригласить 3 друзей",
        "desc": "Поделись своей реферальной ссылкой и пригласи минимум 3 друзей по ссылке.",
    },
    "REF_2": {
        "category": "referral",
        "progress_target": 7,
        "title": "Пригласить 7 друзей",
        "desc": "Расскажи о боте тем, кому он может быть полезен, и приведи 7 друзей по своей ссылке.",
    },
    "REF_3": {
        "category": "referral",
        "progress_target": 15,
        "title": "Пригласить 15 друзей",
        "desc": "Продолжай делиться ссылкой: 15 активных приглашений — хороший вклад в развитие проекта.",
    },
    "REF_4": {
        "category": "referral",
        "progress_target": 30,
        "title": "Пригласить 30 друзей",
        "desc": "Ты создаёшь целое мини‑сообщество вокруг Esoteric AI — пригласи 30 друзей по ссылке.",
    },
    "REF_5": {
        "category": "referral",
        "progress_target": 100,
        "title": "Пригласить 100 друзей",
        "desc": "Самый высокий реферальный уровень: 100 приглашённых друзей и мощный бонус в ответ.",
    },

    # Usage
    "USE_1": {
        "category": "usage",
        "progress_target": 30,
        "title": "30 вопросов боту",
        "desc": "Задай 30 вопросов (Таро + Гороскоп) и познакомься с возможностями бота.",
    },
    "USE_2": {
        "category": "usage",
        "progress_target": 50,
        "title": "50 вопросов боту",
        "desc": "Сделай 50 запросов — чем чаще практикуешь, тем тоньше чувствуешь подсказки.",
    },
    "USE_3": {
        "category": "usage",
        "progress_target": 100,
        "title": "100 вопросов боту",
        "desc": "Сто запросов — это уже целая история взаимодействия с ботом.",
    },
    "USE_4": {
        "category": "usage",
        "progress_target": 300,
        "title": "300 вопросов боту",
        "desc": "Три сотни вопросов — глубинное знакомство с картами и ритуалами.",
    },
    "USE_5": {
        "category": "usage",
        "progress_target": 1000,
        "title": "1000 вопросов боту",
        "desc": "Ты — одна из самых активных участниц проекта. Тысяча вопросов — серьёзный путь.",
    },

    # Purchases
    "BUY_0": {
        "category": "purchases",
        "progress_target": 1,
        "title": "Первая покупка",
        "desc": "Сделай первую покупку сообщений в любом объёме — попробуй, как работает платный доступ.",
    },
    "BUY_1": {
        "category": "purchases",
        "progress_target": 100,
        "title": "Купить 100 платных сообщений",
        "desc": "Собери 100 купленных платных сообщений (за всё время).",
    },
    "BUY_2": {
        "category": "purchases",
        "progress_target": 300,
        "title": "Купить 300 платных сообщений",
        "desc": "Когда есть запас сообщений, можно практиковать глубже и чаще.",
    },
    "BUY_3": {
        "category": "purchases",
        "progress_target": 800,
        "title": "Купить 800 платных сообщений",
        "desc": "800 сообщений — серьёзный кредит доверия к проекту, благодарим за поддержку.",
    },
    "BUY_4": {
        "category": "purchases",
        "progress_target": 1500,
        "title": "Купить 1500 платных сообщений",
        "desc": "Ты одна из самых вовлечённых участниц — твоя практика уже стала частью пути.",
    },
    "BUY_5": {
        "category": "purchases",
        "progress_target": 3000,
        "title": "Купить 3000 платных сообщений",
        "desc": "Максимальный уровень доверия: 3000 купленных сообщений за всё время.",
    },

    # Levels
    "LEVEL_UP_1": {
        "category": "levels",
        "progress_target": 100,
        "title": "Достигнуть уровня 2",
        "desc": "Подними статус до уровня 2 «Ищущая» (100 XP) и получи дополнительную награду.",
    },
    "LEVEL_UP_2": {
        "category": "levels",
        "progress_target": 300,
        "title": "Достигнуть уровня 3",
        "desc": "Дойди до уровня 3 «Посвящённая» (300 XP) — стабильная работа с практиками.",
    },
    "LEVEL_UP_3": {
        "category": "levels",
        "progress_target": 700,
        "title": "Достигнуть уровня 4",
        "desc": "Поднимись до уровня 4 «Хранительница карт» (700 XP) — системная глубинная работа.",
    },
    "LEVEL_UP_4": {
        "category": "levels",
        "progress_target": 1200,
        "title": "Достигнуть уровня 5",
        "desc": "Выйди на уровень 5 «Лунная Жрица» (1200 XP) — практикующий проводник для других.",
    },
    "LEVEL_UP_5": {
        "category": "levels",
        "progress_target": 2000,
        "title": "Достигнуть уровня 6",
        "desc": "Достигни уровня 6 «Ведущая кругов» (2000 XP) — центр своего маленького сообщества.",
    },
    "LEVEL_UP_6": {
        "category": "levels",
        "progress_target": 3000,
        "title": "Достигнуть уровня 7",
        "desc": "Поднимись на уровень 7 «Верховная Мистерия» (3000 XP) — максимальное достижение в системе статусов.",
    },
}

# === НАГРАДЫ ===
TASK_REWARDS: Dict[str, List[Dict[str, Any]]] = {
    "D_DAILY": [{"type": "xp", "amount": 2}],
    "D_REQ_DAILY": [{"type": "xp", "amount": 3}],
    "D_1": [{"type": "xp", "amount": 10}, {"type": "sms", "amount": 1}],
    "D_2": [{"type": "xp", "amount": 30}, {"type": "sms", "amount": 10}],
    "D_3": [
        {"type": "xp", "amount": 30},
        {"type": "sms", "amount": 5},
        {"type": "promocode", "percent": 5},
    ],
    "D_4": [
        {"type": "xp", "amount": 80},
        {"type": "sms", "amount": 15},
        {"type": "promocode", "percent": 10},
    ],
    "D_5": [
        {"type": "xp", "amount": 150},
        {"type": "sms", "amount": 30},
        {"type": "promocode", "percent": 15},
    ],
    "REF_1": [
        {"type": "xp", "amount": 70},
        {"type": "sms", "amount": 10},
        {"type": "promocode", "percent": 5},
    ],
    "REF_2": [
        {"type": "xp", "amount": 120},
        {"type": "sms", "amount": 15},
        {"type": "promocode", "percent": 10},
    ],
    "REF_3": [
        {"type": "xp", "amount": 220},
        {"type": "sms", "amount": 35},
        {"type": "promocode", "percent": 20},
    ],
    "REF_4": [
        {"type": "xp", "amount": 370},
        {"type": "sms", "amount": 75},
        {"type": "promocode", "percent": 25},
    ],
    "REF_5": [
        {"type": "xp", "amount": 900},
        {"type": "sms", "amount": 200},
        {"type": "promocode", "percent": 30},
    ],
    "USE_1": [{"type": "xp", "amount": 50}, {"type": "sms", "amount": 5}],
    "USE_2": [{"type": "xp", "amount": 80}, {"type": "sms", "amount": 10}],
    "USE_3": [
        {"type": "xp", "amount": 150},
        {"type": "sms", "amount": 25},
        {"type": "promocode", "percent": 5},
    ],
    "USE_4": [
        {"type": "xp", "amount": 300},
        {"type": "sms", "amount": 50},
        {"type": "promocode", "percent": 10},
    ],
    "USE_5": [
        {"type": "xp", "amount": 800},
        {"type": "sms", "amount": 150},
        {"type": "promocode", "percent": 25},
    ],
    "BUY_0": [
        {"type": "xp", "amount": 50},
        {"type": "sms", "amount": 5},
        {"type": "promocode", "percent": 3},
    ],
    "BUY_1": [
        {"type": "xp", "amount": 80},
        {"type": "sms", "amount": 10},
        {"type": "promocode", "percent": 5},
    ],
    "BUY_2": [
        {"type": "xp", "amount": 150},
        {"type": "sms", "amount": 30},
        {"type": "promocode", "percent": 10},
    ],
    "BUY_3": [
        {"type": "xp", "amount": 300},
        {"type": "sms", "amount": 80},
        {"type": "promocode", "percent": 20},
    ],
    "BUY_4": [
        {"type": "xp", "amount": 750},
        {"type": "sms", "amount": 150},
        {"type": "promocode", "percent": 25},
    ],
    "BUY_5": [
        {"type": "xp", "amount": 1500},
        {"type": "sms", "amount": 300},
        {"type": "promocode", "percent": 30},
    ],
    "LEVEL_UP_1": [{"type": "xp", "amount": 20}],
    "LEVEL_UP_2": [{"type": "xp", "amount": 30}, {"type": "sms", "amount": 10}],
    "LEVEL_UP_3": [{"type": "xp", "amount": 50}, {"type": "sms", "amount": 30}],
    "LEVEL_UP_4": [{"type": "xp", "amount": 100}, {"type": "sms", "amount": 80}],
    "LEVEL_UP_5": [{"type": "xp", "amount": 150}, {"type": "sms", "amount": 150}],
    "LEVEL_UP_6": [{"type": "xp", "amount": 200}, {"type": "sms", "amount": 200}],
}


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_task_record(user_id: int, task_code: str) -> None:
    """Создаёт запись задачи, если её нет."""
    if task_code not in TASK_CONFIG:
        return
    progress_target = TASK_CONFIG[task_code]["progress_target"]

    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO user_tasks (
                user_id, task_code, progress_current, progress_target, reward_claimed
            )
            VALUES (?, ?, 0, ?, 0)
            ON CONFLICT(user_id, task_code) DO NOTHING
        """,
            (user_id, task_code, progress_target),
        )
        conn.commit()
    finally:
        conn.close()


def _apply_task_reward(user_id: int, task_code: str) -> None:
    """Начисляет награды по задаче и помечает её как полученную (без возврата балансов)."""
    rewards = TASK_REWARDS.get(task_code, [])
    xp_delta = 0
    sms_delta = 0

    for r in rewards:
        if r["type"] == "xp":
            xp_delta += r["amount"]
        elif r["type"] == "sms":
            sms_delta += r["amount"]
        elif r["type"] == "promocode":
            # Промокоды пока не обрабатываем
            pass

    if xp_delta > 0:
        add_user_xp(user_id, xp_delta)
    if sms_delta > 0:
        change_messages_balance(user_id, sms_delta)

    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE user_tasks
            SET reward_claimed = 1
            WHERE user_id = ? AND task_code = ?
        """,
            (user_id, task_code),
        )
        conn.commit()
    finally:
        conn.close()


def increment_task_progress(user_id: int, task_code: str, delta: int = 1) -> None:
    """
    Увеличивает прогресс задачи и, если цель достигнута и награда ещё не выдана,
    автоматически начисляет её.
    """
    if task_code not in TASK_CONFIG:
        return

    ensure_task_record(user_id, task_code)
    conn = _get_connection()
    try:
        cur = conn.cursor()
        # Обновляем прогресс
        cur.execute(
            """
            UPDATE user_tasks
            SET progress_current = MIN(progress_current + ?, ?)
            WHERE user_id = ? AND task_code = ?
        """,
            (delta, TASK_CONFIG[task_code]["progress_target"], user_id, task_code),
        )
        conn.commit()

        # Проверяем, не пора ли выдать награду
        cur.execute(
            """
            SELECT progress_current, progress_target, reward_claimed
            FROM user_tasks
            WHERE user_id = ? AND task_code = ?
        """,
            (user_id, task_code),
        )
        row = cur.fetchone()
        if (
            row
            and not row["reward_claimed"]
            and row["progress_current"] >= row["progress_target"]
        ):
            _apply_task_reward(user_id, task_code)
    finally:
        conn.close()


def get_tasks_by_category(user_id: int, category: str) -> List[Dict[str, Any]]:
    """Возвращает задачи категории в формате фронта."""
    tasks: List[Dict[str, Any]] = []

    for code, cfg in TASK_CONFIG.items():
        if cfg["category"] != category:
            continue

        ensure_task_record(user_id, code)

        conn = _get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT progress_current, reward_claimed
                FROM user_tasks
                WHERE user_id = ? AND task_code = ?
            """,
                (user_id, code),
            )
            row = cur.fetchone()
            progress = row["progress_current"] if row else 0
            claimed = bool(row and row["reward_claimed"])
        finally:
            conn.close()

        target = cfg["progress_target"]

        if claimed:
            status = "completed"
        elif progress >= target:
            # технически награда уже будет выдана при increment_task_progress,
            # но на случай гонок показываем как готовую
            status = "completed"
        elif progress > 0:
            status = "in_progress"
        else:
            status = "pending"

        reward_cfg = TASK_REWARDS.get(code, [])
        xp = sum(r["amount"] for r in reward_cfg if r["type"] == "xp")
        sms = sum(r["amount"] for r in reward_cfg if r["type"] == "sms")
        promo = next(
            (f"{r['percent']}%" for r in reward_cfg if r["type"] == "promocode"),
            None,
        )

        tasks.append(
            {
                "code": code,
                "status": status,
                "progress_current": progress,
                "progress_target": target,
                "reward_claimed": claimed,
                "xp": xp,
                "sms": sms,
                "promo": promo,
                "title": cfg.get("title"),
                "desc": cfg.get("desc"),
            }
        )

    return tasks
