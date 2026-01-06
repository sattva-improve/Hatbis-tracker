"""Habit handlers."""
import logging
from typing import Any, Dict

from .common import (
    create_response,
    error_response,
    parse_body,
    get_path_parameter,
    get_query_parameter,
    require_auth,
    handle_exceptions,
)
from ..services.habit_service import HabitService
from ..models.habit import HabitCategory, HabitDifficulty, FrequencyType, HabitFrequency

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_auth
def list_habits(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """List user's habits."""
    user_id = event["user_id"]
    
    # Parse query parameters
    category = get_query_parameter(event, "category")
    is_active = get_query_parameter(event, "is_active", "true").lower() == "true"
    is_archived = get_query_parameter(event, "is_archived", "false").lower() == "true"
    
    habit_service = HabitService()
    habits = habit_service.list_habits(
        user_id=user_id,
        category=HabitCategory(category) if category else None,
        is_active=is_active,
        is_archived=is_archived,
    )
    
    return create_response(200, {
        "habits": [h.model_dump() for h in habits],
        "total": len(habits),
    })


@handle_exceptions
@require_auth
def create_habit(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Create a new habit."""
    user_id = event["user_id"]
    body = parse_body(event)
    
    # Validate required fields
    name = body.get("name")
    if not name:
        return error_response(400, "MISSING_FIELD", "name は必須です")
    
    # Parse frequency
    frequency_data = body.get("frequency", {})
    frequency = HabitFrequency(
        type=FrequencyType(frequency_data.get("type", "daily")),
        times_per_week=frequency_data.get("times_per_week"),
        specific_days=frequency_data.get("specific_days"),
    )
    
    habit_service = HabitService()
    
    try:
        habit = habit_service.create_habit(
            user_id=user_id,
            name=name,
            description=body.get("description"),
            icon=body.get("icon", "📝"),
            color=body.get("color", "#4CAF50"),
            category=HabitCategory(body.get("category", "other")),
            frequency=frequency,
            difficulty=HabitDifficulty(body.get("difficulty", "normal")),
            reminder_enabled=body.get("reminder_enabled", False),
            reminder_time=body.get("reminder_time"),
        )
        
        return create_response(201, habit.model_dump())
        
    except ValueError as e:
        return error_response(400, "VALIDATION_ERROR", str(e))


@handle_exceptions
@require_auth
def get_habit(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get a specific habit."""
    user_id = event["user_id"]
    habit_id = get_path_parameter(event, "habitId")
    
    if not habit_id:
        return error_response(400, "MISSING_PARAMETER", "habitId は必須です")
    
    habit_service = HabitService()
    habit = habit_service.get_habit(habit_id, user_id)
    
    if not habit:
        return error_response(404, "HABIT_NOT_FOUND", "習慣が見つかりません")
    
    return create_response(200, habit.model_dump())


@handle_exceptions
@require_auth
def update_habit(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Update a habit."""
    user_id = event["user_id"]
    habit_id = get_path_parameter(event, "habitId")
    body = parse_body(event)
    
    if not habit_id:
        return error_response(400, "MISSING_PARAMETER", "habitId は必須です")
    
    # Parse frequency if provided
    frequency = None
    if "frequency" in body:
        frequency_data = body["frequency"]
        frequency = HabitFrequency(
            type=FrequencyType(frequency_data.get("type", "daily")),
            times_per_week=frequency_data.get("times_per_week"),
            specific_days=frequency_data.get("specific_days"),
        )
    
    habit_service = HabitService()
    
    try:
        habit = habit_service.update_habit(
            habit_id=habit_id,
            user_id=user_id,
            name=body.get("name"),
            description=body.get("description"),
            icon=body.get("icon"),
            color=body.get("color"),
            category=HabitCategory(body["category"]) if "category" in body else None,
            frequency=frequency,
            difficulty=HabitDifficulty(body["difficulty"]) if "difficulty" in body else None,
            reminder_enabled=body.get("reminder_enabled"),
            reminder_time=body.get("reminder_time"),
            is_active=body.get("is_active"),
            is_archived=body.get("is_archived"),
        )
        
        if not habit:
            return error_response(404, "HABIT_NOT_FOUND", "習慣が見つかりません")
        
        return create_response(200, habit.model_dump())
        
    except ValueError as e:
        return error_response(400, "VALIDATION_ERROR", str(e))


@handle_exceptions
@require_auth
def delete_habit(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Delete a habit."""
    user_id = event["user_id"]
    habit_id = get_path_parameter(event, "habitId")
    
    if not habit_id:
        return error_response(400, "MISSING_PARAMETER", "habitId は必須です")
    
    habit_service = HabitService()
    success = habit_service.delete_habit(habit_id, user_id)
    
    if not success:
        return error_response(404, "HABIT_NOT_FOUND", "習慣が見つかりません")
    
    return create_response(204)


@handle_exceptions
@require_auth
def archive_habit(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Archive a habit."""
    user_id = event["user_id"]
    habit_id = get_path_parameter(event, "habitId")
    
    if not habit_id:
        return error_response(400, "MISSING_PARAMETER", "habitId は必須です")
    
    habit_service = HabitService()
    habit = habit_service.archive_habit(habit_id, user_id)
    
    if not habit:
        return error_response(404, "HABIT_NOT_FOUND", "習慣が見つかりません")
    
    return create_response(200, habit.model_dump())
