"""Habit record models for Habit Tracker RPG."""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class HabitRecord(BaseModel):
    """Record of a habit completion."""
    
    record_id: str = Field(..., description="Unique record ID")
    habit_id: str = Field(..., description="Associated habit ID")
    user_id: str = Field(..., description="Owner user ID")
    
    # Completion date
    completed_date: date = Field(..., description="Date of completion")
    
    # Details
    completed: bool = Field(default=True)
    note: Optional[str] = Field(default=None, max_length=500)
    
    # EXP earned for this completion
    exp_earned: int = Field(default=0, ge=0)
    
    # Streak at time of completion
    streak_at_completion: int = Field(default=0, ge=0)
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }


class HabitRecordCreate(BaseModel):
    """Request model for creating a habit record."""
    
    habit_id: str
    completed_date: date
    completed: bool = Field(default=True)
    note: Optional[str] = Field(default=None, max_length=500)


class HabitRecordUpdate(BaseModel):
    """Request model for updating a habit record."""
    
    completed: Optional[bool] = None
    note: Optional[str] = Field(None, max_length=500)


class DailyStats(BaseModel):
    """Daily statistics for a user."""
    
    date: date
    total_habits: int = 0
    completed_habits: int = 0
    completion_rate: float = 0.0
    total_exp_earned: int = 0


class WeeklyStats(BaseModel):
    """Weekly statistics for a user."""
    
    week_start: date
    week_end: date
    total_habits: int = 0
    completed_habits: int = 0
    completion_rate: float = 0.0
    total_exp_earned: int = 0
    daily_stats: list[DailyStats] = Field(default_factory=list)


class MonthlyStats(BaseModel):
    """Monthly statistics for a user."""
    
    year: int
    month: int
    total_habits: int = 0
    completed_habits: int = 0
    completion_rate: float = 0.0
    total_exp_earned: int = 0
    weekly_stats: list[WeeklyStats] = Field(default_factory=list)
