"""Job service for job/title management."""
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from ulid import ULID
from boto3.dynamodb.conditions import Key

from ..models.job import Job, UserJob, JobProgress, PREDEFINED_JOBS
from ..models.gamification import StatType
from .dynamodb_repository import DynamoDBRepository
from .user_service import UserService


USER_JOBS_TABLE = os.environ.get("USER_JOBS_TABLE", "habit-tracker-rpg-user-jobs")


class JobService:
    """Service for job operations."""
    
    def __init__(self):
        """Initialize job service."""
        self.user_jobs_repo = DynamoDBRepository(USER_JOBS_TABLE)
        self.user_service = UserService()
    
    def get_all_jobs(self) -> List[Job]:
        """Get all predefined jobs."""
        return PREDEFINED_JOBS
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        for job in PREDEFINED_JOBS:
            if job.job_id == job_id:
                return job
        return None
    
    def get_user_jobs(self, user_id: str) -> List[UserJob]:
        """Get all jobs unlocked by user."""
        items = self.user_jobs_repo.query(
            key_condition=Key("user_id").eq(user_id),
        )
        return [UserJob(**item) for item in items]
    
    def is_job_unlocked(self, user_id: str, job_id: str) -> bool:
        """Check if user has unlocked a job."""
        item = self.user_jobs_repo.get_item({
            "user_id": user_id,
            "job_id": job_id,
        })
        return item is not None
    
    def unlock_job(self, user_id: str, job_id: str) -> Optional[Job]:
        """Unlock a job for a user."""
        job = self.get_job(job_id)
        if not job:
            return None
        
        # Check if already unlocked
        if self.is_job_unlocked(user_id, job_id):
            return None
        
        # Create user job record
        user_job = UserJob(
            user_job_id=str(ULID()),
            user_id=user_id,
            job_id=job_id,
            unlocked_at=datetime.utcnow(),
            is_equipped=False,
        )
        
        self.user_jobs_repo.put_item(user_job.model_dump())
        
        return job
    
    def equip_job(self, user_id: str, job_id: str) -> Any:
        """Equip a job for a user."""
        # Check if job is unlocked
        if not self.is_job_unlocked(user_id, job_id):
            raise ValueError("Job is not unlocked")
        
        # Unequip current job
        user_jobs = self.get_user_jobs(user_id)
        for uj in user_jobs:
            if uj.is_equipped:
                self.user_jobs_repo.update_item(
                    {"user_id": user_id, "job_id": uj.job_id},
                    {"is_equipped": False},
                )
        
        # Equip new job
        self.user_jobs_repo.update_item(
            {"user_id": user_id, "job_id": job_id},
            {"is_equipped": True},
        )
        
        # Update user's current job
        return self.user_service.set_current_job(user_id, job_id)
    
    def check_job_requirements(self, user_id: str, job: Job) -> Dict[str, bool]:
        """Check if user meets job requirements."""
        user = self.user_service.get_user(user_id)
        if not user:
            return {}
        
        requirements = job.requirements
        met = {}
        
        # Check level requirement
        if "level" in requirements:
            met["level"] = user.level >= requirements["level"]
        
        # Check stat requirements
        if "stats" in requirements:
            stat_reqs = requirements["stats"]
            for stat_name, required_level in stat_reqs.items():
                stat_type = StatType(stat_name)
                current_level = user.stats.get_stat(stat_type)
                met[f"stat_{stat_name}"] = current_level >= required_level
        
        # Check achievement requirements
        if "achievements" in requirements:
            from .achievement_service import AchievementService
            achievement_service = AchievementService()
            
            for achievement_id in requirements["achievements"]:
                met[f"achievement_{achievement_id}"] = achievement_service.is_achievement_unlocked(
                    user_id, achievement_id
                )
        
        return met
    
    def check_job_unlocks(self, user_id: str) -> List[Job]:
        """Check and unlock jobs based on current state."""
        unlocked = []
        
        for job in PREDEFINED_JOBS:
            # Skip if already unlocked
            if self.is_job_unlocked(user_id, job.job_id):
                continue
            
            # Check requirements
            requirements_met = self.check_job_requirements(user_id, job)
            
            # Unlock if all requirements met
            if all(requirements_met.values()) if requirements_met else not job.requirements:
                result = self.unlock_job(user_id, job.job_id)
                if result:
                    unlocked.append(result)
        
        return unlocked
    
    def get_job_progress(self, user_id: str, job_id: str) -> Optional[JobProgress]:
        """Get user's progress towards a job."""
        job = self.get_job(job_id)
        if not job:
            return None
        
        # Check if unlocked
        user_job_item = self.user_jobs_repo.get_item({
            "user_id": user_id,
            "job_id": job_id,
        })
        
        is_unlocked = user_job_item is not None
        is_equipped = user_job_item.get("is_equipped", False) if user_job_item else False
        unlocked_at = None
        if user_job_item and "unlocked_at" in user_job_item:
            unlocked_at = datetime.fromisoformat(user_job_item["unlocked_at"])
        
        # Get requirements status
        requirements_met = self.check_job_requirements(user_id, job)
        
        # Get progress details
        progress_details = self._get_job_progress_details(user_id, job)
        
        return JobProgress(
            job_id=job_id,
            job=job,
            is_unlocked=is_unlocked,
            is_equipped=is_equipped,
            unlocked_at=unlocked_at,
            requirements_met=requirements_met,
            progress_details=progress_details,
        )
    
    def _get_job_progress_details(self, user_id: str, job: Job) -> Dict[str, Any]:
        """Get detailed progress towards job requirements."""
        user = self.user_service.get_user(user_id)
        if not user:
            return {}
        
        details = {}
        requirements = job.requirements
        
        if "level" in requirements:
            details["level"] = {
                "current": user.level,
                "required": requirements["level"],
            }
        
        if "stats" in requirements:
            details["stats"] = {}
            for stat_name, required_level in requirements["stats"].items():
                stat_type = StatType(stat_name)
                current_level = user.stats.get_stat(stat_type)
                details["stats"][stat_name] = {
                    "current": current_level,
                    "required": required_level,
                }
        
        return details
    
    def get_all_jobs_progress(
        self,
        user_id: str,
        include_locked: bool = True,
    ) -> List[JobProgress]:
        """Get progress for all jobs."""
        progress_list = []
        
        for job in PREDEFINED_JOBS:
            progress = self.get_job_progress(user_id, job.job_id)
            if progress:
                if include_locked or progress.is_unlocked:
                    progress_list.append(progress)
        
        return progress_list
