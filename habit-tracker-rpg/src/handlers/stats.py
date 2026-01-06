"""Statistics handlers."""
import logging
from datetime import date
from typing import Any, Dict

from .common import (
    create_response,
    error_response,
    get_query_parameter,
    require_auth,
    handle_exceptions,
)
from ..services.stats_service import StatsService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_auth
def get_daily_stats(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get daily statistics."""
    user_id = event["user_id"]
    
    date_str = get_query_parameter(event, "date")
    if not date_str:
        return error_response(400, "MISSING_PARAMETER", "date は必須です")
    
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        return error_response(400, "INVALID_DATE", "date の形式が無効です")
    
    stats_service = StatsService()
    stats = stats_service.get_daily_stats(user_id, target_date)
    
    return create_response(200, stats.model_dump())


@handle_exceptions
@require_auth
def get_weekly_stats(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get weekly statistics."""
    user_id = event["user_id"]
    
    week_start_str = get_query_parameter(event, "week_start")
    if not week_start_str:
        return error_response(400, "MISSING_PARAMETER", "week_start は必須です")
    
    try:
        week_start = date.fromisoformat(week_start_str)
    except ValueError:
        return error_response(400, "INVALID_DATE", "week_start の形式が無効です")
    
    stats_service = StatsService()
    stats = stats_service.get_weekly_stats(user_id, week_start)
    
    return create_response(200, stats.model_dump())


@handle_exceptions
@require_auth
def get_monthly_stats(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get monthly statistics."""
    user_id = event["user_id"]
    
    year_str = get_query_parameter(event, "year")
    month_str = get_query_parameter(event, "month")
    
    if not year_str or not month_str:
        return error_response(400, "MISSING_PARAMETER", "year と month は必須です")
    
    try:
        year = int(year_str)
        month = int(month_str)
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
    except ValueError as e:
        return error_response(400, "INVALID_PARAMETER", str(e))
    
    stats_service = StatsService()
    stats = stats_service.get_monthly_stats(user_id, year, month)
    
    return create_response(200, stats.model_dump())
