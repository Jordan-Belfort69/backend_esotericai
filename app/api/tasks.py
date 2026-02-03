# app/api/tasks.py

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Annotated, Literal
from pydantic import BaseModel
from app.deps.current_user import CurrentUserDep
from app.services.tasks_service import get_tasks_by_category, claim_task_reward

router = APIRouter(prefix="/api")

Category = Literal["daily", "activity", "referral", "usage", "purchases", "levels"]

class TaskClaimRequest(BaseModel):
    task_code: str

@router.get("/tasks/list")
def tasks_list(
    category: Category = Query(...),
    user_id: CurrentUserDep = None,
):
    """
    Возвращает задачи указанной категории.
    """
    tasks = get_tasks_by_category(user_id, category)
    return {
        "category": category,
        "tasks": tasks,
    }

@router.post("/tasks/claim")
def tasks_claim(
    request: TaskClaimRequest,
    user_id: CurrentUserDep = None,
):
    """
    Получает награду за задачу.
    """
    try:
        result = claim_task_reward(user_id, request.task_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))