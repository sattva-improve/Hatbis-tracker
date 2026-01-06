"""Achievement service."""
import os
from datetime import datetime
from typing import List, Optional

from ulid import ULID
from boto3.dynamodb.conditions import Key, Attr

from ..models.achievement import (
    Achievement,
    UserAchievement,
    AchievementProgress,
    AchievementType,
    PREDEFINED_ACHIEVEMENTS,
)
from .dynamodb_repository import DynamoDBRepository
from .user_service import UserService


ACHIEVEMENTS_TABLE = os.environ.get("ACHIEVEMENTS_TABLE", "habit-tracker-rpg-achievements")
USER_ACHIEVEMENTS_TABLE = os.environ.get("USER_ACHIEVEMENTS_TABLE", "habit-tracker-rpg-user-achievements")


class AchievementService:
    """Service for achievement operations."""
    
    def __init__(self):
        """Initialize achievement service."""
        self.achievements_repo = DynamoDBRepository(ACHIEVEMENTS_TABLE)
        self.user_achievements_repo = DynamoDBRepository(USER_ACHIEVEMENTS_TABLE)
        self.user_service = UserService()
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get all predefined achievements."""
        return PREDEFINED_ACHIEVEMENTS
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get achievement by ID."""
        for achievement in PREDEFINED_ACHIEVEMENTS:
            if achievement.achievement_id == achievement_id:
                return achievement
        return None
    
    def get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """Get all achievements unlocked by user."""
        items = self.user_achievements_repo.query(
            key_condition=Key("user_id").eq(user_id),
        )
        return [UserAchievement(**item) for item in items]
    
    def is_achievement_unlocked(self, user_id: str, achievement_id: str) -> bool:
        """Check if user has unlocked an achievement."""
        item = self.user_achievements_repo.get_item({
            "user_id": user_id,
            "achievement_id": achievement_id,
        })
        return item is not None
    
    def unlock_achievement(
        self,
        user_id: str,
        achievement_id: str,
        progress_at_unlock: Optional[dict] = None,
    ) -> Optional[Achievement]:
        """Unlock an achievement for a user."""
        achievement = self.get_achievement(achievement_id)
        if not achievement:
            return None
        
        # Check if already unlocked
        if self.is_achievement_unlocked(user_id, achievement_id):
            return None
        
        # Create user achievement record
        user_achievement = UserAchievement(
            user_achievement_id=str(ULID()),
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=datetime.utcnow(),
            progress_at_unlock=progress_at_unlock,
        )
        
        self.user_achievements_repo.put_item(user_achievement.model_dump())
        
        # Award EXP reward
        if achievement.exp_reward > 0:
            self.user_service.add_experience(user_id, achievement.exp_reward)
        
        return achievement
    
    def check_achievements(self, user_id: str, current_streak: int) -> List[Achievement]:
        """Check and unlock achievements based on current state."""
        user = self.user_service.get_user(user_id)
        if not user:
            return []
        
        unlocked = []
        
        for achievement in PREDEFINED_ACHIEVEMENTS:
            # Skip if already unlocked
            if self.is_achievement_unlocked(user_id, achievement.achievement_id):
                continue
            
            condition = achievement.condition
            should_unlock = False
            
            # Check streak achievements
            if achievement.type == AchievementType.STREAK:
                required_days = condition.get("days", 0)
                if current_streak >= required_days:
                    should_unlock = True
            
            # Check total completion achievements
            elif achievement.type == AchievementType.TOTAL:
                # This would need total completions count
                pass
            
            # Check level achievements
            elif achievement.type == AchievementType.LEVEL:
                required_level = condition.get("level", 0)
                if user.level >= required_level:
                    should_unlock = True
            
            if should_unlock:
                result = self.unlock_achievement(
                    user_id,
                    achievement.achievement_id,
                    {"streak": current_streak, "level": user.level},
                )
                if result:
                    unlocked.append(result)
        
        return unlocked
    
    def check_first_habit(self, user_id: str) -> Optional[Achievement]:
        """Check and unlock first habit achievement."""
        return self.unlock_achievement(user_id, "first_habit")
    
    def check_first_completion(self, user_id: str) -> Optional[Achievement]:
        """Check and unlock first completion achievement."""
        return self.unlock_achievement(user_id, "first_completion")
    
    def get_achievement_progress(
        self,
        user_id: str,
        achievement_id: str,
    ) -> Optional[AchievementProgress]:
        """Get user's progress towards an achievement."""
        achievement = self.get_achievement(achievement_id)
        if not achievement:
            return None
        
        user = self.user_service.get_user(user_id)
        if not user:
            return None
        
        # Check if unlocked
        user_achievement = self.user_achievements_repo.get_item({
            "user_id": user_id,
            "achievement_id": achievement_id,
        })
        
        is_unlocked = user_achievement is not None
        unlocked_at = None
        if user_achievement:
            unlocked_at = datetime.fromisoformat(user_achievement["unlocked_at"])
        
        # Calculate progress
        current_value = 0
        target_value = 0
        
        condition = achievement.condition
        
        if achievement.type == AchievementType.STREAK:
            target_value = condition.get("days", 0)
            current_value = user.current_streak
        elif achievement.type == AchievementType.LEVEL:
            target_value = condition.get("level", 0)
            current_value = user.level
        elif achievement.type == AchievementType.FIRST:
            target_value = 1
            current_value = 1 if is_unlocked else 0
        
        progress_percent = min(current_value / target_value * 100, 100) if target_value > 0 else 0
        
        return AchievementProgress(
            achievement_id=achievement_id,
            achievement=achievement,
            is_unlocked=is_unlocked,
            unlocked_at=unlocked_at,
            current_value=current_value,
            target_value=target_value,
            progress_percent=progress_percent,
        )
    
    def get_all_achievements_progress(
        self,
        user_id: str,
        include_locked: bool = True,
    ) -> List[AchievementProgress]:
        """Get progress for all achievements."""
        progress_list = []
        
        for achievement in PREDEFINED_ACHIEVEMENTS:
            progress = self.get_achievement_progress(user_id, achievement.achievement_id)
            if progress:
                if include_locked or progress.is_unlocked:
                    progress_list.append(progress)
        
        return progress_list
