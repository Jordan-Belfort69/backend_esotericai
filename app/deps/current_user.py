from fastapi import Depends, HTTPException, Request
from typing import Annotated
from app.services.auth_service import ensure_user_exists


async def CurrentUser(request: Request) -> int:
    """
    Получает user_id, который уже положен в request.state.user_id
    middleware-ом validate_telegram_init_data.
    Гарантирует, что пользователь существует в БД.
    """
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        # initData не прошёл валидацию в middleware или не был передан
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Здесь, если нужно, можно подгрузить/обновить пользователя в БД.
    # У тебя ensure_user_exists сейчас требует first_name и т.п.,
    # поэтому либо:
    #  - оставляем запись пользователя в auth_service.validate_init_data,
    #  - либо здесь вообще ничего не делаем.
    # Предлагаю пока не вызывать ensure_user_exists ещё раз,
    # чтобы не городить дополнительную логику.

    return user_id


CurrentUserDep = Annotated[int, Depends(CurrentUser)]
