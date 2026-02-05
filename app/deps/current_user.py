from fastapi import Depends, Query, HTTPException
from typing import Annotated
from app.services.auth_service import validate_init_data, ensure_user_exists


async def CurrentUser(
    initData: Annotated[str | None, Query(alias="initData")] = None,
) -> int:
    """
    Зависимость для получения user_id из валидированного initData.
    Гарантирует, что пользователь существует в БД.
    """
    if not initData:
        raise HTTPException(status_code=400, detail="initData required")
    
    print(f"🔍 Получен initData (первые 50 символов): {initData[:50]}...")

    telegram_user = validate_init_data(initData)
    user_id = telegram_user.user_id

    print(f"✅ Валидирован пользователь: {user_id} ({telegram_user.first_name})")

    # ВАЖНО: передаём photo_url из telegram_user
    ensure_user_exists(
        user_id=user_id,
        first_name=telegram_user.first_name,
        username=telegram_user.username,
        photo_url=telegram_user.photo_url,  # ← вот этого сейчас не хватает
    )

    return user_id


CurrentUserDep = Annotated[int, Depends(CurrentUser)]
