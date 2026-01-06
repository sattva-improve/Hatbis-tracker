"""Record service for habit record management."""
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any

from ulid import ULID
from boto3.dynamodb.conditions import Key, Attr

from ..models.record import HabitRecord
from ..models.gamification import (
    DEFAULT_EXP_GAIN,
    DEFAULT_STREAK_BONUS,
    get_stat_for_category,
)
from .dynamodb_repository import DynamoDBRepository
from .habit_service import HabitService
from .user_service import UserService


TABLE_NAME = os.environ.get("RECORDS_TABLE", "habit-tracker-rpg-records")


class RecordService:
    """Service for habit record operations."""
    
    def __init__(self):
        """Initialize record service."""
        self.repo = DynamoDBRepository(TABLE_NAME)
        self.habit_service = HabitService()
        self.user_service = UserService()
    
    def create_record(
        self,
        habit_id: str,
        user_id: str,
        completed_date: date,
        completed: bool = True,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a habit completion record."""
        # Get habit
        habit = self.habit_service.get_habit(habit_id, user_id)
        if not habit:
            raise KeyError("Habit not found")
        
        # Check for existing record on same date
        existing = self._get_record_by_date(habit_id, user_id, completed_date)
        if existing:
            raise ValueError("Record already exists for this date")
        
        now = datetime.utcnow()
        record_id = str(ULID())
        
        # Calculate streak
        new_streak = self._calculate_streak(habit_id, user_id, completed_date, completed)
        
        # Calculate EXP
        exp_earned = 0
        if completed:
            exp_earned = DEFAULT_EXP_GAIN.calculate_exp(
                difficulty=habit.difficulty.value,
                streak_days=new_streak,
                streak_bonus=DEFAULT_STREAK_BONUS,
            )
        
        # Create record
        record = HabitRecord(
            record_id=record_id,
            habit_id=habit_id,
            user_id=user_id,
            completed_date=completed_date,
            completed=completed,
            note=note,
            exp_earned=exp_earned,
            streak_at_completion=new_streak,
            created_at=now,
        )
        
        self.repo.put_item(record.model_dump())
        
        result = {
            "record": record,
            "exp_gained": exp_earned,
            "new_streak": new_streak,
            "level_up": False,
            "new_level": None,
            "stat_level_up": False,
            "new_stat_level": None,
            "stat_type": None,
            "new_achievements": [],
            "new_jobs": [],
        }
        
        if completed and exp_earned > 0:
            # Update habit streak
            self.habit_service.update_streak(habit_id, user_id, new_streak, now)
            
            # Add experience to user
            stat_type = habit.stat_type.value.lower()
            exp_result = self.user_service.add_experience(
                user_id=user_id,
                exp=exp_earned,
                stat_type=stat_type,
            )
            
            result["level_up"] = exp_result["level_up"]
            result["new_level"] = exp_result["new_level"]
            result["stat_level_up"] = exp_result["stat_level_up"]
            result["new_stat_level"] = exp_result["new_stat_level"]
            result["stat_type"] = habit.stat_type.value
            
            # Update user streak
            self.user_service.update_streak(user_id, new_streak)
            
            # Check for achievements
            from .achievement_service import AchievementService
            achievement_service = AchievementService()
            new_achievements = achievement_service.check_achievements(user_id, new_streak)
            result["new_achievements"] = new_achievements
            
            # Check for first completion achievement
            if habit.total_completions == 0:
                first_achievement = achievement_service.check_first_completion(user_id)
                if first_achievement:
                    result["new_achievements"].append(first_achievement)
            
            # Check for new jobs
            from .job_service import JobService
            job_service = JobService()
            new_jobs = job_service.check_job_unlocks(user_id)
            result["new_jobs"] = new_jobs
        
        return result
    
    def _get_record_by_date(
        self,
        habit_id: str,
        user_id: str,
        target_date: date,
    ) -> Optional[HabitRecord]:
        """Get record for a specific date."""
        items = self.repo.query(
            key_condition=Key("habit_id").eq(habit_id),
            filter_expression=Attr("completed_date").eq(target_date.isoformat()),
        )
        
        for item in items:
            if item.get("user_id") == user_id:
                return HabitRecord(**item)
        return None
    
    def _calculate_streak(
        self,
        habit_id: str,
        user_id: str,
        target_date: date,
        completed: bool,
    ) -> int:
        """Calculate streak for a habit."""
        if not completed:
            return 0
        
        # Get habit
        habit = self.habit_service.get_habit(habit_id, user_id)
        if not habit:
            return 0
        
        # Check previous day
        previous_date = target_date - timedelta(days=1)
        previous_record = self._get_record_by_date(habit_id, user_id, previous_date)
        
        if previous_record and previous_record.completed:
            return previous_record.streak_at_completion + 1
        
        return 1
    
    def get_record(
        self,
        record_id: str,
        habit_id: str,
        user_id: str,
    ) -> Optional[HabitRecord]:
        """Get record by ID."""
        item = self.repo.get_item({"habit_id": habit_id, "record_id": record_id})
        if not item or item.get("user_id") != user_id:
            return None
        return HabitRecord(**item)
    
    def list_records(
        self,
        habit_id: str,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[HabitRecord]:
        """List records for a habit."""
        filter_parts = [Attr("user_id").eq(user_id)]
        
        if start_date:
            filter_parts.append(Attr("completed_date").gte(start_date.isoformat()))
        
        if end_date:
            filter_parts.append(Attr("completed_date").lte(end_date.isoformat()))
        
        filter_expression = filter_parts[0]
        for part in filter_parts[1:]:
            filter_expression = filter_expression & part
        
        items = self.repo.query(
            key_condition=Key("habit_id").eq(habit_id),
            filter_expression=filter_expression,
        )
        
        return [HabitRecord(**item) for item in items]
    
    def update_record(
        self,
        record_id: str,
        habit_id: str,
        user_id: str,
        completed: Optional[bool] = None,
        note: Optional[str] = None,
    ) -> Optional[HabitRecord]:
        """Update a record."""
        # Verify ownership
        existing = self.get_record(record_id, habit_id, user_id)
        if not existing:
            return None
        
        updates = {}
        if completed is not None:
            updates["completed"] = completed
        if note is not None:
            updates["note"] = note
        
        if not updates:
            return existing
        
        updated = self.repo.update_item(
            {"habit_id": habit_id, "record_id": record_id},
            updates,
        )
        
        if updated:
            return HabitRecord(**updated)
        return None
    
    def delete_record(
        self,
        record_id: str,
        habit_id: str,
        user_id: str,
    ) -> bool:
        """Delete a record."""
        # Verify ownership
        existing = self.get_record(record_id, habit_id, user_id)
        if not existing:
            return False
        
        return self.repo.delete_item({"habit_id": habit_id, "record_id": record_id})
    
    def get_today_status(self, user_id: str) -> Dict[str, Any]:
        """Get today's habit status for a user."""
        today = date.today()
        
        # Get all active habits
        habits = self.habit_service.list_habits(user_id, is_active=True, is_archived=False)
        
        result = {
            "date": today.isoformat(),
            "habits": [],
            "completed_count": 0,
            "total_due": 0,
            "completion_rate": 0.0,
        }
        
        for habit in habits:
            # Check if habit is due today
            is_due = habit.frequency.is_due_on_day(today.weekday())
            
            # Get today's record if exists
            record = self._get_record_by_date(habit.habit_id, user_id, today)
            
            if is_due:
                result["total_due"] += 1
                if record and record.completed:
                    result["completed_count"] += 1
            
            result["habits"].append({
                "habit": habit.model_dump(),
                "record": record.model_dump() if record else None,
                "is_due_today": is_due,
            })
        
        if result["total_due"] > 0:
            result["completion_rate"] = result["completed_count"] / result["total_due"]
        
        return result
