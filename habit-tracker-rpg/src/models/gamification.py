"""Gamification models and configurations."""
from enum import Enum
from typing import Dict, List
from pydantic import BaseModel, Field


class StatType(str, Enum):
    """Types of RPG stats."""
    
    VITALITY = "VIT"      # 体力 - 運動、睡眠、健康管理
    INTELLIGENCE = "INT"  # 知力 - 読書、勉強、資格学習
    MENTAL = "MND"        # 精神力 - 瞑想、日記、感謝
    DEXTERITY = "DEX"     # 器用さ - 楽器、絵、クラフト
    CHARISMA = "CHA"      # 魅力 - コミュニケーション、身だしなみ
    STRENGTH = "STR"      # 筋力 - 筋トレ、スポーツ


class LevelConfig(BaseModel):
    """Configuration for level calculation.
    
    60日でカンスト（レベル99到達）を目指す設計:
    - 1日3習慣（Normal）を60日連続達成で約2,700 EXP獲得
    - レベル99到達に必要な累計EXP: 約2,700 EXP
    - 序盤は素早く成長、後半は緩やかに
    """
    
    # Base EXP required for level 2
    base_exp: int = Field(default=15)
    
    # Growth rate per level (linear growth for balanced progression)
    growth_rate: float = Field(default=1.02)
    
    # Maximum level
    max_level: int = Field(default=99)
    
    def exp_for_level(self, level: int) -> int:
        """Calculate total EXP required for a specific level.
        
        60日カンスト設計:
        - レベル1→2: 15 EXP
        - レベル50: 約1,000 EXP
        - レベル99: 約2,700 EXP
        """
        if level <= 1:
            return 0
        total = 0
        for lvl in range(2, level + 1):
            total += int(self.base_exp * (self.growth_rate ** (lvl - 2)))
        return total
    
    def level_from_exp(self, exp: int) -> int:
        """Calculate level from total EXP."""
        level = 1
        while level < self.max_level:
            required = self.exp_for_level(level + 1)
            if exp < required:
                break
            level += 1
        return level
    
    def exp_to_next_level(self, current_exp: int) -> int:
        """Calculate EXP needed for next level."""
        current_level = self.level_from_exp(current_exp)
        if current_level >= self.max_level:
            return 0
        next_level_exp = self.exp_for_level(current_level + 1)
        return next_level_exp - current_exp


class StreakBonus(BaseModel):
    """Configuration for streak bonuses."""
    
    # Bonus multipliers based on streak days
    bonuses: Dict[int, float] = Field(default={
        3: 1.1,    # 3日連続: 10%ボーナス
        7: 1.25,   # 7日連続: 25%ボーナス
        14: 1.5,   # 14日連続: 50%ボーナス
        30: 2.0,   # 30日連続: 100%ボーナス
        60: 2.5,   # 60日連続: 150%ボーナス
        90: 3.0,   # 90日連続: 200%ボーナス
    })
    
    def get_multiplier(self, streak_days: int) -> float:
        """Get the bonus multiplier for a given streak."""
        multiplier = 1.0
        for days, bonus in sorted(self.bonuses.items()):
            if streak_days >= days:
                multiplier = bonus
            else:
                break
        return multiplier


class ExpGain(BaseModel):
    """Experience gain configuration.
    
    60日カンスト設計の基本EXP:
    - 基本EXP: 15
    - 1日3習慣 × Normal(1.0) = 45 EXP/日（ストリーク無し）
    - ストリーク30日以上で 45 × 2.0 = 90 EXP/日
    """
    
    # Base EXP for completing a habit
    base_exp: int = Field(default=15)
    
    # Bonus for difficulty
    difficulty_multipliers: Dict[str, float] = Field(default={
        "easy": 0.5,
        "normal": 1.0,
        "hard": 1.5,
        "very_hard": 2.0,
    })
    
    def calculate_exp(
        self,
        difficulty: str = "normal",
        streak_days: int = 0,
        streak_bonus: StreakBonus = None
    ) -> int:
        """Calculate EXP gained for completing a habit."""
        if streak_bonus is None:
            streak_bonus = StreakBonus()
        
        difficulty_mult = self.difficulty_multipliers.get(difficulty, 1.0)
        streak_mult = streak_bonus.get_multiplier(streak_days)
        
        return int(self.base_exp * difficulty_mult * streak_mult)


# Default configurations
DEFAULT_LEVEL_CONFIG = LevelConfig()
DEFAULT_STREAK_BONUS = StreakBonus()
DEFAULT_EXP_GAIN = ExpGain()


# Stat to category mapping
STAT_CATEGORY_MAPPING: Dict[StatType, List[str]] = {
    StatType.VITALITY: ["exercise", "sleep", "health"],
    StatType.INTELLIGENCE: ["reading", "study", "learning"],
    StatType.MENTAL: ["meditation", "journaling", "gratitude", "mindfulness"],
    StatType.DEXTERITY: ["music", "art", "craft", "hobby"],
    StatType.CHARISMA: ["communication", "social", "grooming"],
    StatType.STRENGTH: ["workout", "sports", "fitness"],
}


def get_stat_for_category(category: str) -> StatType:
    """Get the stat type associated with a habit category."""
    category_lower = category.lower()
    for stat_type, categories in STAT_CATEGORY_MAPPING.items():
        if category_lower in categories:
            return stat_type
    # Default to mental if category not found
    return StatType.MENTAL
