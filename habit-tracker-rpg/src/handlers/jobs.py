"""Job handlers."""
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
from ..services.job_service import JobService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@handle_exceptions
@require_auth
def list_jobs(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """List all jobs with user's progress."""
    user_id = event["user_id"]
    
    include_locked = get_query_parameter(event, "include_locked", "true").lower() == "true"
    
    job_service = JobService()
    progress_list = job_service.get_all_jobs_progress(user_id, include_locked)
    
    unlocked_count = sum(1 for p in progress_list if p.is_unlocked)
    
    return create_response(200, {
        "jobs": [p.model_dump() for p in progress_list],
        "unlocked_count": unlocked_count,
        "total_count": len(progress_list),
    })


@handle_exceptions
@require_auth
def get_job(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get a specific job with progress."""
    user_id = event["user_id"]
    job_id = get_path_parameter(event, "jobId")
    
    if not job_id:
        return error_response(400, "MISSING_PARAMETER", "jobId は必須です")
    
    job_service = JobService()
    progress = job_service.get_job_progress(user_id, job_id)
    
    if not progress:
        return error_response(404, "JOB_NOT_FOUND", "ジョブが見つかりません")
    
    return create_response(200, progress.model_dump())


@handle_exceptions
@require_auth
def equip_job(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Equip a job."""
    user_id = event["user_id"]
    job_id = get_path_parameter(event, "jobId")
    
    if not job_id:
        return error_response(400, "MISSING_PARAMETER", "jobId は必須です")
    
    job_service = JobService()
    
    try:
        user = job_service.equip_job(user_id, job_id)
        return create_response(200, user.model_dump())
    except ValueError as e:
        return error_response(400, "CANNOT_EQUIP", str(e))
    except KeyError as e:
        return error_response(404, "NOT_FOUND", str(e))
