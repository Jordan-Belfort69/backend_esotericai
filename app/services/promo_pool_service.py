# app/services/promo_pool_service.py

from typing import Optional, Dict, List

from app.promo_pools.promo_pool_5 import PROMO_CODES as POOL_5
from app.promo_pools.promo_pool_10 import PROMO_CODES as POOL_10
from app.promo_pools.promo_pool_15 import PROMO_CODES as POOL_15
from app.promo_pools.promo_pool_20 import PROMO_CODES as POOL_20
from app.promo_pools.promo_pool_25 import PROMO_CODES as POOL_25
from app.promo_pools.promo_pool_30 import PROMO_CODES as POOL_30

_POOL_MAP: Dict[int, List[str]] = {
    5: POOL_5,
    10: POOL_10,
    15: POOL_15,
    20: POOL_20,
    25: POOL_25,
    30: POOL_30,
}

def get_promo_from_pool(discount_percent: int) -> Optional[str]:
    """
    Возвращает один промокод из пула для указанной скидки.
    Пока просто берём первый код из списка.
    """
    pool = _POOL_MAP.get(discount_percent)
    if not pool:
        return None
    return pool[0] if pool else None
