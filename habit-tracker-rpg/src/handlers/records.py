"""Habit record handlers."""
import logging
from datetime import date, datetime
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
from ..services.record_service import RecordService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_auth
def list_habit_records(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """List records for a habit."""
    user_id = event["user_id"]
    habit_id = get_path_parameter(event, "habitId")
    
    if not habit_id:
        return error_response(400, "MISSING_PARAMETER", "habitId は必須です")
    
    # Parse date range
    start_date_str = get_query_parameter(event, "start_date")
    end_date_str = get_query_parameter(event, "end_date")
    
    start_date = date.fromisoformat(start_date_str) if start_date_str else None
    end_date = date.fromisoformat(end_date_str) if end_date_str else None
    
    record_service = RecordService()
    records = record_service.list_records(
        habit_id=habit_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    return create_response(200, {
        "records": [r.model_dump() for r in records],
        "total": len(records),
    })


@handle_exceptions
@require_auth
def create_habit_record(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Record a habit completion."""
    user_id = event["user_id"]
    habit_id = get_path_parameter(event, "habitId")
    body = parse_body(event)
    
    if not habit_id:
        return error_response(400, "MISSING_PARAMETER", "habitId は必須です")
    
    completed_date_str = body.get("completed_date")
    if not completed_date_str:
        return error_response(400, "MISSING_FIELD", "completed_date は必須です")
    
    try:
        completed_date = date.fromisoformat(completed_date_str)
    except ValueError:
        return error_response(400, "INVALID_DATE", "completed_date の形式が無効です")
    
    record_service = RecordService()
    
    try:
        result = record_service.create_record(
            habit_id=habit_id,
            user_id=user_id,
            completed_date=completed_date,
            completed=body.get("completed", True),
            note=body.get("note"),
        )
        
        return create_response(201, {
            "record": result["record"].model_dump(),
            "exp_gained": result["exp_gained"],
            "new_streak": result["new_streak"],
            "level_up": result["level_up"],
            "new_level": result["new_level"],
            "stat_level_up": result["stat_level_up"],
            "new_stat_level": result["new_stat_level"],
            "stat_type": result["stat_type"],
            "new_achievements": [a.model_dump() for a in result.get("new_achievements", [])],
            "new_jobs": [j.model_dump() for j in result.get("new_jobs", [])],
        })
        
    except ValueError as e:
        return error_response(400, "VALIDATION_ERROR", str(e))
    except KeyError as e:
        return error_response(404, "NOT_FOUND", str(e))


@handle_exceptions
@require_auth
def update_habit_record(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Update a habit record."""
    user_id = event["user_id"]
    habit_id = get_path_parameter(event, "habitId")
    record_id = get_path_parameter(event, "recordId")
    body = parse_body(event)
    
    if not habit_id or not record_id:
        return error_response(400, "MISSING_PARAMETER", "habitId と recordId は必須です")
    
    record_service = RecordService()
    
    try:
        record = record_service.update_record(
            record_id=record_id,
            habit_id=habit_id,
            user_id=user_id,
            completed=body.get("completed"),
            note=body.get("note"),
        )
        
        if not record:
            return error_response(404, "RECORD_NOT_FOUND", "記録が見つかりません")
        
        return create_response(200, record.model_dump())
        
    except ValueError as e:
        return error_response(400, "VALIDATION_ERROR", str(e))


@handle_exceptions
@require_auth
def delete_habit_record(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Delete a habit record."""
    user_id = event["user_id"]
    habit_id = get_path_parameter(event, "habitId")
    record_id = get_path_parameter(event, "recordId")
    
    if not habit_id or not record_id:
        return error_response(400, "MISSING_PARAMETER", "habitId と recordId は必須です")
    
    record_service = RecordService()
    success = record_service.delete_record(record_id, habit_id, user_id)
    
    if not success:
        return error_response(404, "RECORD_NOT_FOUND", "記録が見つかりません")
    
    return create_response(204)


@handle_exceptions
@require_auth
def get_today_records(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get today's habit status."""
    user_id = event["user_id"]
    
    record_service = RecordService()
    today_status = record_service.get_today_status(user_id)
    
    return create_response(200, today_status)
