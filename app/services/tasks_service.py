# ===== ИСПРАВЛЕННЫЙ КОД =====
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Literal
from core.config import DB_PATH
from app.services.user_balance_service import change_messages_balance, add_user_xp, get_messages_balance, get_user_xp

# === КОНФИГ ЗАДАЧ (дублирует фронт, но для сервера) ===
TASK_CONFIG = {
    # Daily
    "D_DAILY": {"category": "daily", "progress_target": 1},
    "D_REQ_DAILY": {"category": "daily", "progress_target": 1},
    # Activity
    "D_1": {"category": "activity", "progress_target": 1},
    "D_2": {"category": "activity", "progress_target": 1},
    "D_3": {"category": "activity", "progress_target": 1},
    "D_4": {"category": "activity", "progress_target": 1},
    "D_5": {"category": "activity", "progress_target": 1},
    # Referral
    "REF_1": {"category": "referral", "progress_target": 1},
    "REF_2": {"category": "referral", "progress_target": 2},
    "REF_3": {"category": "referral", "progress_target": 3},
    "REF_4": {"category": "referral", "progress_target": 4},
    "REF_5": {"category": "referral", "progress_target": 5},
    # Usage
    "USE_1": {"category": "usage", "progress_target": 5},
    "USE_2": {"category": "usage", "progress_target": 10},
    "USE_3": {"category": "usage", "progress_target": 20},
    "USE_4": {"category": "usage", "progress_target": 30},
    "USE_5": {"category": "usage", "progress_target": 50},
    # Purchases
    "BUY_0": {"category": "purchases", "progress_target": 1},
    "BUY_1": {"category": "purchases", "progress_target": 1},
    "BUY_2": {"category": "purchases", "progress_target": 1},
    "BUY_3": {"category": "purchases", "progress_target": 1},
    "BUY_4": {"category": "purchases", "progress_target": 1},
    "BUY_5": {"category": "purchases", "progress_target": 1},
    # Levels
    "LEVEL_UP_1": {"category": "levels", "progress_target": 1},
    "LEVEL_UP_2": {"category": "levels", "progress_target": 1},
    "LEVEL_UP_3": {"category": "levels", "progress_target": 1},
    "LEVEL_UP_4": {"category": "levels", "progress_target": 1},
    "LEVEL_UP_5": {"category": "levels", "progress_target": 1},
    "LEVEL_UP_6": {"category": "levels", "progress_target": 1},
}

# === НАГРАДЫ ===
TASK_REWARDS = {
    "D_DAILY": [{"type": "xp", "amount": 2}],
    "D_REQ_DAILY": [{"type": "xp", "amount": 3}],
    "D_1": [{"type": "xp", "amount": 10}, {"type": "sms", "amount": 1}],
    "D_2": [{"type": "xp", "amount": 30}, {"type": "sms", "amount": 10}],
    "D_3": [{"type": "xp", "amount": 30}, {"type": "sms", "amount": 5}, {"type": "promocode", "percent": 5}],
    "D_4": [{"type": "xp", "amount": 80}, {"type": "sms", "amount": 15}, {"type": "promocode", "percent": 10}],
    "D_5": [{"type": "xp", "amount": 150}, {"type": "sms", "amount": 30}, {"type": "promocode", "percent": 15}],
    "REF_1": [{"type": "xp", "amount": 70}, {"type": "sms", "amount": 10}, {"type": "promocode", "percent": 5}],
    "REF_2": [{"type": "xp", "amount": 120}, {"type": "sms", "amount": 15}, {"type": "promocode", "percent": 10}],
    "REF_3": [{"type": "xp", "amount": 220}, {"type": "sms", "amount": 35}, {"type": "promocode", "percent": 20}],
    "REF_4": [{"type": "xp", "amount": 370}, {"type": "sms", "amount": 75}, {"type": "promocode", "percent": 25}],
    "REF_5": [{"type": "xp", "amount": 900}, {"type": "sms", "amount": 200}, {"type": "promocode", "percent": 30}],
    "USE_1": [{"type": "xp", "amount": 50}, {"type": "sms", "amount": 5}],
    "USE_2": [{"type": "xp", "amount": 80}, {"type": "sms", "amount": 10}],
    "USE_3": [{"type": "xp", "amount": 150}, {"type": "sms", "amount": 25}, {"type": "promocode", "percent": 5}],
    "USE_4": [{"type": "xp", "amount": 300}, {"type": "sms", "amount": 50}, {"type": "promocode", "percent": 10}],
    "USE_5": [{"type": "xp", "amount": 800}, {"type": "sms", "amount": 150}, {"type": "promocode", "percent": 25}],
    "BUY_0": [{"type": "xp", "amount": 50}, {"type": "sms", "amount": 5}, {"type": "promocode", "percent": 3}],
    "BUY_1": [{"type": "xp", "amount": 80}, {"type": "sms", "amount": 10}, {"type": "promocode", "percent": 5}],
    "BUY_2": [{"type": "xp", "amount": 150}, {"type": "sms", "amount": 30}, {"type": "promocode", "percent": 10}],
    "BUY_3": [{"type": "xp", "amount": 300}, {"type": "sms", "amount": 80}, {"type": "promocode", "percent": 20}],
    "BUY_4": [{"type": "xp", "amount": 750}, {"type": "sms", "amount": 150}, {"type": "promocode", "percent": 25}],
    "BUY_5": [{"type": "xp", "amount": 1500}, {"type": "sms", "amount": 300}, {"type": "promocode", "percent": 30}],
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
        cur.execute("""
            INSERT INTO user_tasks (
                user_id, task_code, progress_current, progress_target, reward_claimed
            )
            VALUES (?, ?, 0, ?, 0)
            ON CONFLICT(user_id, task_code) DO NOTHING
        """, (user_id, task_code, progress_target))
        conn.commit()
    finally:
        conn.close()

def increment_task_progress(user_id: int, task_code: str, delta: int = 1) -> None:
    """Увеличивает прогресс задачи."""
    ensure_task_record(user_id, task_code)
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE user_tasks
            SET progress_current = MIN(progress_current + ?, ?)
            WHERE user_id = ? AND task_code = ?
        """, (delta, TASK_CONFIG[task_code]["progress_target"], user_id, task_code))
        conn.commit()
    finally:
        conn.close()

def get_tasks_by_category(user_id: int, category: str) -> List[Dict[str, Any]]:
    """Возвращает задачи категории в формате фронта."""
    tasks = []
    for code, cfg in TASK_CONFIG.items():
        if cfg["category"] != category:
            continue
        ensure_task_record(user_id, code)
        conn = _get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT progress_current, reward_claimed
                FROM user_tasks
                WHERE user_id = ? AND task_code = ?
            """, (user_id, code))
            row = cur.fetchone()
            progress = row["progress_current"] if row else 0
            claimed = bool(row and row["reward_claimed"])
        finally:
            conn.close()
        
        target = cfg["progress_target"]
        if claimed:
            status = "completed"
        elif progress >= target:
            status = "ready_to_claim"
        elif progress > 0:
            status = "in_progress"
        else:
            status = "pending"

        tasks.append({
            "code": code,
            "status": status,
            "progress_current": progress,
            "progress_target": target,
        })
    return tasks

def is_task_claimable(user_id: int, task_code: str) -> bool:
    if task_code not in TASK_CONFIG:
        return False
    ensure_task_record(user_id, task_code)
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT progress_current, reward_claimed
            FROM user_tasks
            WHERE user_id = ? AND task_code = ?
        """, (user_id, task_code))
        row = cur.fetchone()
        if not row or row["reward_claimed"]:
            return False
        progress = row["progress_current"]
        target = TASK_CONFIG[task_code]["progress_target"]
        return progress >= target
    finally:
        conn.close()

def claim_task_reward(user_id: int, task_code: str) -> Dict[str, Any]:
    """Начисляет награды и возвращает новые балансы."""
    if not is_task_claimable(user_id, task_code):
        raise ValueError("Task not claimable")
    
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

    # Помечаем как получено
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE user_tasks
            SET reward_claimed = 1
            WHERE user_id = ? AND task_code = ?
        """, (user_id, task_code))
        conn.commit()
    finally:
        conn.close()

    return {
        "ok": True,
        "new_xp": get_user_xp(user_id),
        "new_credits_balance": get_messages_balance(user_id),
    }