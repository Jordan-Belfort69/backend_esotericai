# app/api/tasks.py

from fastapi import APIRouter, Query
from typing import Literal
from app.deps.current_user import CurrentUserDep
from app.services.tasks_service import get_tasks_by_category

router = APIRouter(prefix="/api")

Category = Literal["daily", "activity", "referral", "usage", "purchases", "levels"]


@router.get("/tasks/list")
def tasks_list(
    category: Category = Query(...),
    user_id: CurrentUserDep = None,
):
    """
    Возвращает задачи указанной категории.
    Награды за задачи начисляются автоматически при достижении прогресса
    (см. increment_task_progress в tasks_service).
    """
    tasks = get_tasks_by_category(user_id, category)
    return {
        "category": category,
        "tasks": tasks,
    }
