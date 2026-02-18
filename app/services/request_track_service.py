# app/services/request_track_service.py

from app.services.tasks_service import increment_task_progress


async def track_user_request(user_id: int, request_type: str) -> None:
    """
    Общая точка учёта любого запроса к ИИ.
    Двигает ежедневные и долгосрочные задачи.
    """
    # ежедневный запрос
    await increment_task_progress(user_id, "D_REQ_DAILY")

    # долгосрочное использование (кол-во запросов за всё время)
    await increment_task_progress(user_id, "USE_1")
    await increment_task_progress(user_id, "USE_2")
    await increment_task_progress(user_id, "USE_3")
    await increment_task_progress(user_id, "USE_4")
    await increment_task_progress(user_id, "USE_5")
