"""User service for user management."""
import os
from datetime import datetime
from typing import Optional

from ulid import ULID
from boto3.dynamodb.conditions import Key

from ..models.user import User, UserProfile, UserStats
from ..models.gamification import DEFAULT_LEVEL_CONFIG
from ..models.job import PREDEFINED_JOBS
from .dynamodb_repository import DynamoDBRepository


TABLE_NAME = os.environ.get("USERS_TABLE", "habit-tracker-rpg-users")


class UserService:
    """Service for user operations."""
    
    def __init__(self):
        """Initialize user service."""
        self.repo = DynamoDBRepository(TABLE_NAME)
    
    def create_user(
        self,
        user_id: str,
        email: str,
        display_name: str,
        timezone: str = "Asia/Tokyo",
    ) -> User:
        """Create a new user."""
        now = datetime.utcnow()
        
        # Create user with default stats and beginner job
        user = User(
            user_id=user_id,
            email=email,
            profile=UserProfile(
                display_name=display_name,
                timezone=timezone,
            ),
            stats=UserStats(),
            level=1,
            total_exp=0,
            current_job_id="beginner",
            created_at=now,
            updated_at=now,
        )
        
        self.repo.put_item(user.model_dump())
        
        # Unlock beginner job
        from .job_service import JobService
        job_service = JobService()
        job_service.unlock_job(user_id, "beginner")
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        item = self.repo.get_item({"user_id": user_id})
        if not item:
            return None
        return User(**item)
    
    def update_user(
        self,
        user_id: str,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> Optional[User]:
        """Update user profile."""
        user = self.get_user(user_id)
        if not user:
            return None
        
        updates = {"updated_at": datetime.utcnow()}
        
        # Update profile fields
        profile_updates = {}
        if display_name is not None:
            profile_updates["display_name"] = display_name
        if avatar_url is not None:
            profile_updates["avatar_url"] = avatar_url
        if bio is not None:
            profile_updates["bio"] = bio
        if timezone is not None:
            profile_updates["timezone"] = timezone
        
        if profile_updates:
            new_profile = user.profile.model_dump()
            new_profile.update(profile_updates)
            updates["profile"] = new_profile
        
        updated = self.repo.update_item(
            {"user_id": user_id},
            updates,
        )
        
        if updated:
            return User(**updated)
        return None
    
    def add_experience(
        self,
        user_id: str,
        exp: int,
        stat_type: Optional[str] = None,
    ) -> dict:
        """Add experience to user and check for level up."""
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        result = {
            "level_up": False,
            "new_level": user.level,
            "stat_level_up": False,
            "new_stat_level": None,
        }
        
        # Add total exp
        new_total_exp = user.total_exp + exp
        new_level = DEFAULT_LEVEL_CONFIG.level_from_exp(new_total_exp)
        
        if new_level > user.level:
            result["level_up"] = True
            result["new_level"] = new_level
        
        updates = {
            "total_exp": new_total_exp,
            "level": new_level,
            "updated_at": datetime.utcnow(),
        }
        
        # Add stat exp if specified
        if stat_type:
            stats = user.stats.model_dump()
            stat_exp_key = f"{stat_type.lower()}_exp"
            stat_level_key = stat_type.lower()
            
            if stat_exp_key in stats:
                new_stat_exp = stats[stat_exp_key] + exp
                new_stat_level = DEFAULT_LEVEL_CONFIG.level_from_exp(new_stat_exp)
                
                if new_stat_level > stats[stat_level_key]:
                    result["stat_level_up"] = True
                    result["new_stat_level"] = new_stat_level
                
                stats[stat_exp_key] = new_stat_exp
                stats[stat_level_key] = new_stat_level
                updates["stats"] = stats
        
        self.repo.update_item({"user_id": user_id}, updates)
        
        return result
    
    def update_streak(self, user_id: str, new_streak: int) -> None:
        """Update user's streak."""
        user = self.get_user(user_id)
        if not user:
            return
        
        updates = {
            "current_streak": new_streak,
            "updated_at": datetime.utcnow(),
        }
        
        if new_streak > user.max_streak:
            updates["max_streak"] = new_streak
        
        self.repo.update_item({"user_id": user_id}, updates)
    
    def set_current_job(self, user_id: str, job_id: str) -> Optional[User]:
        """Set user's current job."""
        updated = self.repo.update_item(
            {"user_id": user_id},
            {
                "current_job_id": job_id,
                "updated_at": datetime.utcnow(),
            },
        )
        
        if updated:
            return User(**updated)
        return None
