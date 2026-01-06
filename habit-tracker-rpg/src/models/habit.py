"""Habit models for Habit Tracker RPG."""
from datetime import datetime, time
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from .gamification import StatType


class HabitCategory(str, Enum):
    """Categories for habits."""
    
    # Vitality (VIT)
    EXERCISE = "exercise"
    SLEEP = "sleep"
    HEALTH = "health"
    
    # Intelligence (INT)
    READING = "reading"
    STUDY = "study"
    LEARNING = "learning"
    
    # Mental (MND)
    MEDITATION = "meditation"
    JOURNALING = "journaling"
    GRATITUDE = "gratitude"
    MINDFULNESS = "mindfulness"
    
    # Dexterity (DEX)
    MUSIC = "music"
    ART = "art"
    CRAFT = "craft"
    HOBBY = "hobby"
    
    # Charisma (CHA)
    COMMUNICATION = "communication"
    SOCIAL = "social"
    GROOMING = "grooming"
    
    # Strength (STR)
    WORKOUT = "workout"
    SPORTS = "sports"
    FITNESS = "fitness"
    
    # Other
    OTHER = "other"


class FrequencyType(str, Enum):
    """Types of habit frequency."""
    
    DAILY = "daily"           # 毎日
    WEEKLY = "weekly"         # 週N回
    SPECIFIC_DAYS = "specific_days"  # 特定の曜日


class HabitFrequency(BaseModel):
    """Habit frequency configuration."""
    
    type: FrequencyType = Field(default=FrequencyType.DAILY)
    
    # For WEEKLY: target times per week
    times_per_week: Optional[int] = Field(default=None, ge=1, le=7)
    
    # For SPECIFIC_DAYS: list of weekdays (0=Monday, 6=Sunday)
    specific_days: Optional[List[int]] = Field(default=None)

    def is_due_on_day(self, weekday: int) -> bool:
        """Check if habit is due on a specific weekday."""
        if self.type == FrequencyType.DAILY:
            return True
        elif self.type == FrequencyType.SPECIFIC_DAYS:
            return weekday in (self.specific_days or [])
        elif self.type == FrequencyType.WEEKLY:
            # For weekly habits, they can be done any day
            return True
        return False


class HabitDifficulty(str, Enum):
    """Difficulty levels for habits."""
    
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    VERY_HARD = "very_hard"


class Habit(BaseModel):
    """Habit model."""
    
    habit_id: str = Field(..., description="Unique habit ID")
    user_id: str = Field(..., description="Owner user ID")
    
    # Basic info
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    icon: Optional[str] = Field(default="📝")
    color: Optional[str] = Field(default="#4CAF50")
    
    # Category and stat
    category: HabitCategory = Field(default=HabitCategory.OTHER)
    stat_type: StatType = Field(default=StatType.MENTAL)
    
    # Frequency
    frequency: HabitFrequency = Field(default_factory=HabitFrequency)
    
    # Difficulty (affects EXP gain)
    difficulty: HabitDifficulty = Field(default=HabitDifficulty.NORMAL)
    
    # Reminder settings
    reminder_enabled: bool = Field(default=False)
    reminder_time: Optional[time] = None
    
    # Tracking
    current_streak: int = Field(default=0, ge=0)
    best_streak: int = Field(default=0, ge=0)
    total_completions: int = Field(default=0, ge=0)
    
    # Status
    is_active: bool = Field(default=True)
    is_archived: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_completed_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            time: lambda v: v.isoformat() if v else None,
        }


class HabitCreate(BaseModel):
    """Request model for creating a habit."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    icon: Optional[str] = Field(default="📝")
    color: Optional[str] = Field(default="#4CAF50")
    category: HabitCategory = Field(default=HabitCategory.OTHER)
    frequency: HabitFrequency = Field(default_factory=HabitFrequency)
    difficulty: HabitDifficulty = Field(default=HabitDifficulty.NORMAL)
    reminder_enabled: bool = Field(default=False)
    reminder_time: Optional[time] = None


class HabitUpdate(BaseModel):
    """Request model for updating a habit."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = None
    color: Optional[str] = None
    category: Optional[HabitCategory] = None
    frequency: Optional[HabitFrequency] = None
    difficulty: Optional[HabitDifficulty] = None
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[time] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None
