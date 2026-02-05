# app/services/__init__.py

from .auth_service import validate_init_data, ensure_user_exists
from .user_service import get_user_profile
from .history_service import list_history, get_history_detail
from .tasks_service import get_tasks_by_category, increment_task_progress
from .referrals_service import get_referrals_info
from .promocodes_service import get_promocodes_for_user
from .limits_service import get_today_limits
