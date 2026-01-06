"""User handlers."""
import logging
from typing import Any, Dict

from .common import (
    create_response,
    error_response,
    parse_body,
    require_auth,
    handle_exceptions,
)
from ..services.user_service import UserService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_auth
def get_my_profile(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get current user's profile."""
    user_id = event["user_id"]
    
    user_service = UserService()
    user = user_service.get_user(user_id)
    
    if not user:
        return error_response(404, "USER_NOT_FOUND", "ユーザーが見つかりません")
    
    return create_response(200, user.model_dump())


@handle_exceptions
@require_auth
def update_my_profile(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Update current user's profile."""
    user_id = event["user_id"]
    body = parse_body(event)
    
    user_service = UserService()
    
    try:
        user = user_service.update_user(
            user_id=user_id,
            display_name=body.get("display_name"),
            avatar_url=body.get("avatar_url"),
            bio=body.get("bio"),
            timezone=body.get("timezone"),
        )
        
        if not user:
            return error_response(404, "USER_NOT_FOUND", "ユーザーが見つかりません")
        
        return create_response(200, user.model_dump())
        
    except ValueError as e:
        return error_response(400, "VALIDATION_ERROR", str(e))


@handle_exceptions
@require_auth
def get_my_stats(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get current user's stats."""
    user_id = event["user_id"]
    
    user_service = UserService()
    user = user_service.get_user(user_id)
    
    if not user:
        return error_response(404, "USER_NOT_FOUND", "ユーザーが見つかりません")
    
    # Calculate next level EXP for each stat
    from ..models.gamification import DEFAULT_LEVEL_CONFIG
    
    stats_response = {
        "vitality": user.stats.vitality,
        "vitality_exp": user.stats.vitality_exp,
        "vitality_next_level_exp": DEFAULT_LEVEL_CONFIG.exp_to_next_level(user.stats.vitality_exp),
        "intelligence": user.stats.intelligence,
        "intelligence_exp": user.stats.intelligence_exp,
        "intelligence_next_level_exp": DEFAULT_LEVEL_CONFIG.exp_to_next_level(user.stats.intelligence_exp),
        "mental": user.stats.mental,
        "mental_exp": user.stats.mental_exp,
        "mental_next_level_exp": DEFAULT_LEVEL_CONFIG.exp_to_next_level(user.stats.mental_exp),
        "dexterity": user.stats.dexterity,
        "dexterity_exp": user.stats.dexterity_exp,
        "dexterity_next_level_exp": DEFAULT_LEVEL_CONFIG.exp_to_next_level(user.stats.dexterity_exp),
        "charisma": user.stats.charisma,
        "charisma_exp": user.stats.charisma_exp,
        "charisma_next_level_exp": DEFAULT_LEVEL_CONFIG.exp_to_next_level(user.stats.charisma_exp),
        "strength": user.stats.strength,
        "strength_exp": user.stats.strength_exp,
        "strength_next_level_exp": DEFAULT_LEVEL_CONFIG.exp_to_next_level(user.stats.strength_exp),
    }
    
    return create_response(200, stats_response)
