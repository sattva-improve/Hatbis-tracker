"""User models for Habit Tracker RPG."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from .gamification import StatType


class UserStats(BaseModel):
    """User's RPG stats."""
    
    vitality: int = Field(default=1, ge=1, description="体力 (VIT) - 運動、睡眠、健康管理")
    intelligence: int = Field(default=1, ge=1, description="知力 (INT) - 読書、勉強、資格学習")
    mental: int = Field(default=1, ge=1, description="精神力 (MND) - 瞑想、日記、感謝")
    dexterity: int = Field(default=1, ge=1, description="器用さ (DEX) - 楽器、絵、クラフト")
    charisma: int = Field(default=1, ge=1, description="魅力 (CHA) - コミュニケーション、身だしなみ")
    strength: int = Field(default=1, ge=1, description="筋力 (STR) - 筋トレ、スポーツ")
    
    # Experience points for each stat
    vitality_exp: int = Field(default=0, ge=0)
    intelligence_exp: int = Field(default=0, ge=0)
    mental_exp: int = Field(default=0, ge=0)
    dexterity_exp: int = Field(default=0, ge=0)
    charisma_exp: int = Field(default=0, ge=0)
    strength_exp: int = Field(default=0, ge=0)

    def get_stat(self, stat_type: StatType) -> int:
        """Get stat value by type."""
        stat_map = {
            StatType.VITALITY: self.vitality,
            StatType.INTELLIGENCE: self.intelligence,
            StatType.MENTAL: self.mental,
            StatType.DEXTERITY: self.dexterity,
            StatType.CHARISMA: self.charisma,
            StatType.STRENGTH: self.strength,
        }
        return stat_map.get(stat_type, 1)

    def get_exp(self, stat_type: StatType) -> int:
        """Get experience points by stat type."""
        exp_map = {
            StatType.VITALITY: self.vitality_exp,
            StatType.INTELLIGENCE: self.intelligence_exp,
            StatType.MENTAL: self.mental_exp,
            StatType.DEXTERITY: self.dexterity_exp,
            StatType.CHARISMA: self.charisma_exp,
            StatType.STRENGTH: self.strength_exp,
        }
        return exp_map.get(stat_type, 0)


class UserProfile(BaseModel):
    """User profile information."""
    
    display_name: str = Field(..., min_length=1, max_length=50)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=500)
    timezone: str = Field(default="Asia/Tokyo")


class User(BaseModel):
    """User model."""
    
    user_id: str = Field(..., description="Cognito User ID")
    email: EmailStr
    profile: UserProfile
    stats: UserStats = Field(default_factory=UserStats)
    
    # Overall level
    level: int = Field(default=1, ge=1)
    total_exp: int = Field(default=0, ge=0)
    
    # Current job/title
    current_job_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    
    # Streak tracking
    max_streak: int = Field(default=0, ge=0)
    current_streak: int = Field(default=0, ge=0)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserCreate(BaseModel):
    """Request model for creating a user."""
    
    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=50)
    timezone: str = Field(default="Asia/Tokyo")


class UserUpdate(BaseModel):
    """Request model for updating a user."""
    
    display_name: Optional[str] = Field(None, min_length=1, max_length=50)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = None
