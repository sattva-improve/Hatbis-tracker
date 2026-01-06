"""Statistics service."""
import os
from datetime import date, timedelta
from typing import Dict, List, Any

from boto3.dynamodb.conditions import Key, Attr

from ..models.record import DailyStats, WeeklyStats, MonthlyStats
from .dynamodb_repository import DynamoDBRepository
from .habit_service import HabitService


RECORDS_TABLE = os.environ.get("RECORDS_TABLE", "habit-tracker-rpg-records")


class StatsService:
    """Service for statistics operations."""
    
    def __init__(self):
        """Initialize stats service."""
        self.records_repo = DynamoDBRepository(RECORDS_TABLE)
        self.habit_service = HabitService()
    
    def get_daily_stats(self, user_id: str, target_date: date) -> DailyStats:
        """Get daily statistics."""
        habits = self.habit_service.list_habits(user_id, is_active=True, is_archived=False)
        
        total_habits = 0
        completed_habits = 0
        total_exp = 0
        habit_completions = []
        
        for habit in habits:
            # Check if habit was due on this date
            if not habit.frequency.is_due_on_day(target_date.weekday()):
                continue
            
            total_habits += 1
            
            # Find record for this date
            items = self.records_repo.query(
                key_condition=Key("habit_id").eq(habit.habit_id),
                filter_expression=Attr("completed_date").eq(target_date.isoformat()) & Attr("user_id").eq(user_id),
            )
            
            record = items[0] if items else None
            completed = record and record.get("completed", False) if record else False
            exp_earned = record.get("exp_earned", 0) if record else 0
            
            if completed:
                completed_habits += 1
                total_exp += exp_earned
            
            habit_completions.append({
                "habit_id": habit.habit_id,
                "habit_name": habit.name,
                "completed": completed,
                "exp_earned": exp_earned,
            })
        
        completion_rate = completed_habits / total_habits if total_habits > 0 else 0.0
        
        return DailyStats(
            date=target_date,
            total_habits=total_habits,
            completed_habits=completed_habits,
            completion_rate=completion_rate,
            total_exp_earned=total_exp,
        )
    
    def get_weekly_stats(self, user_id: str, week_start: date) -> WeeklyStats:
        """Get weekly statistics."""
        # Ensure week_start is a Monday
        week_start = week_start - timedelta(days=week_start.weekday())
        week_end = week_start + timedelta(days=6)
        
        daily_stats = []
        total_habits = 0
        completed_habits = 0
        total_exp = 0
        
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_stats = self.get_daily_stats(user_id, day)
            daily_stats.append(day_stats)
            
            total_habits += day_stats.total_habits
            completed_habits += day_stats.completed_habits
            total_exp += day_stats.total_exp_earned
        
        completion_rate = completed_habits / total_habits if total_habits > 0 else 0.0
        
        return WeeklyStats(
            week_start=week_start,
            week_end=week_end,
            total_habits=total_habits,
            completed_habits=completed_habits,
            completion_rate=completion_rate,
            total_exp_earned=total_exp,
            daily_stats=daily_stats,
        )
    
    def get_monthly_stats(self, user_id: str, year: int, month: int) -> MonthlyStats:
        """Get monthly statistics."""
        from calendar import monthrange
        
        # Get first and last day of month
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        
        weekly_stats = []
        total_habits = 0
        completed_habits = 0
        total_exp = 0
        
        # Get stats for each week
        current_week_start = first_day - timedelta(days=first_day.weekday())
        
        while current_week_start <= last_day:
            week_stats = self.get_weekly_stats(user_id, current_week_start)
            weekly_stats.append(week_stats)
            
            total_habits += week_stats.total_habits
            completed_habits += week_stats.completed_habits
            total_exp += week_stats.total_exp_earned
            
            current_week_start += timedelta(days=7)
        
        completion_rate = completed_habits / total_habits if total_habits > 0 else 0.0
        
        return MonthlyStats(
            year=year,
            month=month,
            total_habits=total_habits,
            completed_habits=completed_habits,
            completion_rate=completion_rate,
            total_exp_earned=total_exp,
            weekly_stats=weekly_stats,
        )
