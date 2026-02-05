from fastapi import Depends, HTTPException, Request
from typing import Annotated


async def CurrentUser(request: Request) -> int:
    """
    Получает user_id, который middleware положил в request.state.user_id.
    """
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user_id


CurrentUserDep = Annotated[int, Depends(CurrentUser)]
