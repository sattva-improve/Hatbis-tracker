"""Achievement handlers."""
import logging
from typing import Any, Dict

from .common import (
    create_response,
    error_response,
    get_path_parameter,
    get_query_parameter,
    require_auth,
    handle_exceptions,
)
from ..services.achievement_service import AchievementService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_auth
def list_achievements(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """List all achievements with user's progress."""
    user_id = event["user_id"]
    
    include_locked = get_query_parameter(event, "include_locked", "true").lower() == "true"
    
    achievement_service = AchievementService()
    progress_list = achievement_service.get_all_achievements_progress(user_id, include_locked)
    
    unlocked_count = sum(1 for p in progress_list if p.is_unlocked)
    
    return create_response(200, {
        "achievements": [p.model_dump() for p in progress_list],
        "unlocked_count": unlocked_count,
        "total_count": len(progress_list),
    })


@handle_exceptions
@require_auth
def get_achievement(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get a specific achievement with progress."""
    user_id = event["user_id"]
    achievement_id = get_path_parameter(event, "achievementId")
    
    if not achievement_id:
        return error_response(400, "MISSING_PARAMETER", "achievementId は必須です")
    
    achievement_service = AchievementService()
    progress = achievement_service.get_achievement_progress(user_id, achievement_id)
    
    if not progress:
        return error_response(404, "ACHIEVEMENT_NOT_FOUND", "アチーブメントが見つかりません")
    
    return create_response(200, progress.model_dump())
