# ===== ИСПРАВЛЕННЫЙ КОД =====
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.config import DB_PATH
from datetime import datetime

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def log_event(
    user_id: int,
    event_type: str,
    question: str,
    answer_full: str,
    meta_json: Optional[Dict] = None
) -> int:
    """Записывает событие в историю."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        # Обрезаем ответ для превью (первые 100 символов)
        answer_short = answer_full[:100] + "..." if len(answer_full) > 100 else answer_full
        
        cur.execute("""
            INSERT INTO history 
            (user_id, type, question, answer_full, answer_short, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            event_type,
            question,
            answer_full,
            answer_short,
            datetime.utcnow().isoformat()
        ))
        
        event_id = cur.lastrowid
        conn.commit()
        
        return event_id
    finally:
        conn.close()

def list_history(user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Возвращает список событий истории."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, type, question, answer_short, created_at
            FROM history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        
        rows = cur.fetchall()
        
        return [
            {
                "id": row["id"],
                "type": row["type"],
                "created_at": row["created_at"],
                "question": row["question"],
                "answer_preview": row["answer_short"],
            }
            for row in rows
        ]
    finally:
        conn.close()

def get_history_detail(user_id: int, event_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает полную запись истории."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, type, question, answer_full, created_at
            FROM history
            WHERE id = ? AND user_id = ?
        """, (event_id, user_id))
        
        row = cur.fetchone()
        
        if not row:
            return None
        
        return {
            "id": row["id"],
            "type": row["type"],
            "created_at": row["created_at"],
            "question": row["question"],
            "answer_full": row["answer_full"],
        }
    finally:
        conn.close()