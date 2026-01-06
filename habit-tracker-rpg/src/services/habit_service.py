"""Habit service for habit management."""
import os
from datetime import datetime, time
from typing import List, Optional

from ulid import ULID
from boto3.dynamodb.conditions import Key, Attr

from ..models.habit import (
    Habit,
    HabitCategory,
    HabitFrequency,
    HabitDifficulty,
)
from ..models.gamification import get_stat_for_category
from .dynamodb_repository import DynamoDBRepository


TABLE_NAME = os.environ.get("HABITS_TABLE", "habit-tracker-rpg-habits")


class HabitService:
    """Service for habit operations."""
    
    def __init__(self):
        """Initialize habit service."""
        self.repo = DynamoDBRepository(TABLE_NAME)
    
    def create_habit(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        icon: str = "📝",
        color: str = "#4CAF50",
        category: HabitCategory = HabitCategory.OTHER,
        frequency: Optional[HabitFrequency] = None,
        difficulty: HabitDifficulty = HabitDifficulty.NORMAL,
        reminder_enabled: bool = False,
        reminder_time: Optional[str] = None,
    ) -> Habit:
        """Create a new habit."""
        now = datetime.utcnow()
        habit_id = str(ULID())
        
        if frequency is None:
            frequency = HabitFrequency()
        
        # Determine stat type from category
        stat_type = get_stat_for_category(category.value)
        
        # Parse reminder time if provided
        parsed_reminder_time = None
        if reminder_time:
            try:
                parsed_reminder_time = time.fromisoformat(reminder_time)
            except ValueError:
                pass
        
        habit = Habit(
            habit_id=habit_id,
            user_id=user_id,
            name=name,
            description=description,
            icon=icon,
            color=color,
            category=category,
            stat_type=stat_type,
            frequency=frequency,
            difficulty=difficulty,
            reminder_enabled=reminder_enabled,
            reminder_time=parsed_reminder_time,
            created_at=now,
            updated_at=now,
        )
        
        # Serialize for DynamoDB
        item = habit.model_dump()
        item["reminder_time"] = reminder_time  # Store as string
        
        self.repo.put_item(item)
        
        # Check for first habit achievement
        from .achievement_service import AchievementService
        achievement_service = AchievementService()
        achievement_service.check_first_habit(user_id)
        
        return habit
    
    def get_habit(self, habit_id: str, user_id: str) -> Optional[Habit]:
        """Get habit by ID."""
        item = self.repo.get_item({"habit_id": habit_id, "user_id": user_id})
        if not item:
            return None
        return Habit(**item)
    
    def list_habits(
        self,
        user_id: str,
        category: Optional[HabitCategory] = None,
        is_active: bool = True,
        is_archived: bool = False,
    ) -> List[Habit]:
        """List user's habits."""
        # Build filter expression
        filter_parts = []
        
        if is_active is not None:
            filter_parts.append(Attr("is_active").eq(is_active))
        
        if is_archived is not None:
            filter_parts.append(Attr("is_archived").eq(is_archived))
        
        if category is not None:
            filter_parts.append(Attr("category").eq(category.value))
        
        filter_expression = None
        if filter_parts:
            filter_expression = filter_parts[0]
            for part in filter_parts[1:]:
                filter_expression = filter_expression & part
        
        items = self.repo.query(
            key_condition=Key("user_id").eq(user_id),
            filter_expression=filter_expression,
            index_name="user_id-index",
        )
        
        return [Habit(**item) for item in items]
    
    def update_habit(
        self,
        habit_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        category: Optional[HabitCategory] = None,
        frequency: Optional[HabitFrequency] = None,
        difficulty: Optional[HabitDifficulty] = None,
        reminder_enabled: Optional[bool] = None,
        reminder_time: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> Optional[Habit]:
        """Update a habit."""
        updates = {"updated_at": datetime.utcnow()}
        
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if icon is not None:
            updates["icon"] = icon
        if color is not None:
            updates["color"] = color
        if category is not None:
            updates["category"] = category.value
            updates["stat_type"] = get_stat_for_category(category.value).value
        if frequency is not None:
            updates["frequency"] = frequency.model_dump()
        if difficulty is not None:
            updates["difficulty"] = difficulty.value
        if reminder_enabled is not None:
            updates["reminder_enabled"] = reminder_enabled
        if reminder_time is not None:
            updates["reminder_time"] = reminder_time
        if is_active is not None:
            updates["is_active"] = is_active
        if is_archived is not None:
            updates["is_archived"] = is_archived
        
        updated = self.repo.update_item(
            {"habit_id": habit_id, "user_id": user_id},
            updates,
        )
        
        if updated:
            return Habit(**updated)
        return None
    
    def delete_habit(self, habit_id: str, user_id: str) -> bool:
        """Delete a habit."""
        return self.repo.delete_item({"habit_id": habit_id, "user_id": user_id})
    
    def archive_habit(self, habit_id: str, user_id: str) -> Optional[Habit]:
        """Archive a habit."""
        return self.update_habit(habit_id, user_id, is_archived=True, is_active=False)
    
    def update_streak(
        self,
        habit_id: str,
        user_id: str,
        new_streak: int,
        completed_at: datetime,
    ) -> Optional[Habit]:
        """Update habit's streak."""
        habit = self.get_habit(habit_id, user_id)
        if not habit:
            return None
        
        updates = {
            "current_streak": new_streak,
            "last_completed_at": completed_at,
            "total_completions": habit.total_completions + 1,
            "updated_at": datetime.utcnow(),
        }
        
        if new_streak > habit.best_streak:
            updates["best_streak"] = new_streak
        
        updated = self.repo.update_item(
            {"habit_id": habit_id, "user_id": user_id},
            updates,
        )
        
        if updated:
            return Habit(**updated)
        return None
