"""Achievement models for Habit Tracker RPG."""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AchievementType(str, Enum):
    """Types of achievements."""
    
    STREAK = "streak"           # 連続達成系
    TOTAL = "total"             # 累計達成系
    LEVEL = "level"             # レベル達成系
    STAT = "stat"               # ステータス達成系
    SPECIAL = "special"         # 特別な達成
    FIRST = "first"             # 初めて系


class AchievementRarity(str, Enum):
    """Rarity of achievements."""
    
    COMMON = "common"           # コモン
    UNCOMMON = "uncommon"       # アンコモン
    RARE = "rare"               # レア
    EPIC = "epic"               # エピック
    LEGENDARY = "legendary"     # レジェンダリー


class Achievement(BaseModel):
    """Achievement definition."""
    
    achievement_id: str = Field(..., description="Unique achievement ID")
    
    # Basic info
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    icon: str = Field(default="🏆")
    
    # Type and rarity
    type: AchievementType
    rarity: AchievementRarity = Field(default=AchievementRarity.COMMON)
    
    # Unlock conditions
    condition: Dict[str, Any] = Field(default_factory=dict)
    # Examples:
    # {"type": "streak", "days": 7}
    # {"type": "total_completions", "count": 100}
    # {"type": "level", "level": 10}
    # {"type": "stat", "stat": "STR", "level": 10}
    
    # Rewards
    exp_reward: int = Field(default=0, ge=0)
    
    # Hidden until unlocked
    is_hidden: bool = Field(default=False)
    
    # Order for display
    sort_order: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserAchievement(BaseModel):
    """User's unlocked achievement."""
    
    user_achievement_id: str = Field(..., description="Unique ID")
    user_id: str = Field(..., description="User who unlocked")
    achievement_id: str = Field(..., description="Achievement that was unlocked")
    
    # Unlock details
    unlocked_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Progress at unlock time (for display)
    progress_at_unlock: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AchievementProgress(BaseModel):
    """Progress towards an achievement."""
    
    achievement_id: str
    achievement: Achievement
    is_unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    
    # Current progress
    current_value: int = 0
    target_value: int = 0
    progress_percent: float = 0.0


# Predefined achievements
PREDEFINED_ACHIEVEMENTS = [
    # Streak achievements
    Achievement(
        achievement_id="streak_3",
        name="三日坊主突破",
        description="3日連続で習慣を達成する",
        icon="🔥",
        type=AchievementType.STREAK,
        rarity=AchievementRarity.COMMON,
        condition={"type": "streak", "days": 3},
        exp_reward=50,
    ),
    Achievement(
        achievement_id="streak_7",
        name="一週間の習慣",
        description="7日連続で習慣を達成する",
        icon="🔥",
        type=AchievementType.STREAK,
        rarity=AchievementRarity.UNCOMMON,
        condition={"type": "streak", "days": 7},
        exp_reward=100,
    ),
    Achievement(
        achievement_id="streak_30",
        name="月間マスター",
        description="30日連続で習慣を達成する",
        icon="🔥",
        type=AchievementType.STREAK,
        rarity=AchievementRarity.RARE,
        condition={"type": "streak", "days": 30},
        exp_reward=500,
    ),
    Achievement(
        achievement_id="streak_100",
        name="百日の道",
        description="100日連続で習慣を達成する",
        icon="💯",
        type=AchievementType.STREAK,
        rarity=AchievementRarity.EPIC,
        condition={"type": "streak", "days": 100},
        exp_reward=2000,
    ),
    Achievement(
        achievement_id="streak_365",
        name="年間王者",
        description="365日連続で習慣を達成する",
        icon="👑",
        type=AchievementType.STREAK,
        rarity=AchievementRarity.LEGENDARY,
        condition={"type": "streak", "days": 365},
        exp_reward=10000,
    ),
    
    # Total completions
    Achievement(
        achievement_id="total_10",
        name="はじめの一歩",
        description="習慣を合計10回達成する",
        icon="👣",
        type=AchievementType.TOTAL,
        rarity=AchievementRarity.COMMON,
        condition={"type": "total_completions", "count": 10},
        exp_reward=30,
    ),
    Achievement(
        achievement_id="total_100",
        name="習慣の達人",
        description="習慣を合計100回達成する",
        icon="⭐",
        type=AchievementType.TOTAL,
        rarity=AchievementRarity.UNCOMMON,
        condition={"type": "total_completions", "count": 100},
        exp_reward=200,
    ),
    Achievement(
        achievement_id="total_1000",
        name="千の習慣",
        description="習慣を合計1000回達成する",
        icon="🌟",
        type=AchievementType.TOTAL,
        rarity=AchievementRarity.RARE,
        condition={"type": "total_completions", "count": 1000},
        exp_reward=1000,
    ),
    
    # Level achievements
    Achievement(
        achievement_id="level_10",
        name="成長の証",
        description="レベル10に到達する",
        icon="📈",
        type=AchievementType.LEVEL,
        rarity=AchievementRarity.UNCOMMON,
        condition={"type": "level", "level": 10},
        exp_reward=150,
    ),
    Achievement(
        achievement_id="level_50",
        name="熟練者",
        description="レベル50に到達する",
        icon="🎯",
        type=AchievementType.LEVEL,
        rarity=AchievementRarity.RARE,
        condition={"type": "level", "level": 50},
        exp_reward=1000,
    ),
    
    # First achievements
    Achievement(
        achievement_id="first_habit",
        name="最初の習慣",
        description="最初の習慣を作成する",
        icon="🎉",
        type=AchievementType.FIRST,
        rarity=AchievementRarity.COMMON,
        condition={"type": "first_habit"},
        exp_reward=20,
    ),
    Achievement(
        achievement_id="first_completion",
        name="最初の達成",
        description="初めて習慣を達成する",
        icon="✅",
        type=AchievementType.FIRST,
        rarity=AchievementRarity.COMMON,
        condition={"type": "first_completion"},
        exp_reward=20,
    ),
]
