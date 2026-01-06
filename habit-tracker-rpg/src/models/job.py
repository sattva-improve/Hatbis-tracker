"""Job/Title models for Habit Tracker RPG."""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .gamification import StatType


class JobTier(str, Enum):
    """Tiers of jobs."""
    
    NOVICE = "novice"           # 初心者
    APPRENTICE = "apprentice"   # 見習い
    JOURNEYMAN = "journeyman"   # 熟練者
    EXPERT = "expert"           # 専門家
    MASTER = "master"           # マスター
    GRANDMASTER = "grandmaster" # グランドマスター


class Job(BaseModel):
    """Job/Title definition."""
    
    job_id: str = Field(..., description="Unique job ID")
    
    # Basic info
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., max_length=500)
    icon: str = Field(default="👤")
    
    # Tier
    tier: JobTier = Field(default=JobTier.NOVICE)
    
    # Requirements to unlock
    requirements: Dict[str, Any] = Field(default_factory=dict)
    # Examples:
    # {"level": 10}
    # {"stats": {"STR": 10, "VIT": 10}}
    # {"achievements": ["streak_30"]}
    
    # Stat bonuses when equipped
    stat_bonuses: Dict[str, int] = Field(default_factory=dict)
    # Example: {"STR": 2, "VIT": 1}
    
    # EXP bonus multiplier
    exp_bonus: float = Field(default=1.0)
    
    # Order for display
    sort_order: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserJob(BaseModel):
    """User's unlocked job."""
    
    user_job_id: str = Field(..., description="Unique ID")
    user_id: str = Field(..., description="User who unlocked")
    job_id: str = Field(..., description="Job that was unlocked")
    
    # Unlock details
    unlocked_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Is this the currently equipped job
    is_equipped: bool = Field(default=False)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JobProgress(BaseModel):
    """Progress towards unlocking a job."""
    
    job_id: str
    job: Job
    is_unlocked: bool = False
    is_equipped: bool = False
    unlocked_at: Optional[datetime] = None
    
    # Requirements progress
    requirements_met: Dict[str, bool] = Field(default_factory=dict)
    progress_details: Dict[str, Any] = Field(default_factory=dict)


# Predefined jobs
PREDEFINED_JOBS = [
    # Novice tier (starting jobs)
    Job(
        job_id="beginner",
        name="ビギナー",
        description="すべての冒険者の始まり",
        icon="🌱",
        tier=JobTier.NOVICE,
        requirements={},
        stat_bonuses={},
        exp_bonus=1.0,
        sort_order=0,
    ),
    
    # Apprentice tier
    Job(
        job_id="warrior_apprentice",
        name="見習い戦士",
        description="筋力を鍛える者",
        icon="⚔️",
        tier=JobTier.APPRENTICE,
        requirements={"stats": {"STR": 5}},
        stat_bonuses={"STR": 1},
        exp_bonus=1.05,
        sort_order=10,
    ),
    Job(
        job_id="scholar_apprentice",
        name="見習い学者",
        description="知識を求める者",
        icon="📚",
        tier=JobTier.APPRENTICE,
        requirements={"stats": {"INT": 5}},
        stat_bonuses={"INT": 1},
        exp_bonus=1.05,
        sort_order=11,
    ),
    Job(
        job_id="monk_apprentice",
        name="見習い修行僧",
        description="心を鍛える者",
        icon="🧘",
        tier=JobTier.APPRENTICE,
        requirements={"stats": {"MND": 5}},
        stat_bonuses={"MND": 1},
        exp_bonus=1.05,
        sort_order=12,
    ),
    Job(
        job_id="athlete_apprentice",
        name="見習いアスリート",
        description="体力を鍛える者",
        icon="🏃",
        tier=JobTier.APPRENTICE,
        requirements={"stats": {"VIT": 5}},
        stat_bonuses={"VIT": 1},
        exp_bonus=1.05,
        sort_order=13,
    ),
    Job(
        job_id="artist_apprentice",
        name="見習いアーティスト",
        description="技巧を磨く者",
        icon="🎨",
        tier=JobTier.APPRENTICE,
        requirements={"stats": {"DEX": 5}},
        stat_bonuses={"DEX": 1},
        exp_bonus=1.05,
        sort_order=14,
    ),
    Job(
        job_id="speaker_apprentice",
        name="見習い話術師",
        description="人々を魅了する者",
        icon="🎤",
        tier=JobTier.APPRENTICE,
        requirements={"stats": {"CHA": 5}},
        stat_bonuses={"CHA": 1},
        exp_bonus=1.05,
        sort_order=15,
    ),
    
    # Journeyman tier
    Job(
        job_id="warrior",
        name="戦士",
        description="強き肉体を持つ者",
        icon="🗡️",
        tier=JobTier.JOURNEYMAN,
        requirements={"stats": {"STR": 15, "VIT": 10}},
        stat_bonuses={"STR": 2, "VIT": 1},
        exp_bonus=1.1,
        sort_order=20,
    ),
    Job(
        job_id="scholar",
        name="学者",
        description="知識の探求者",
        icon="🎓",
        tier=JobTier.JOURNEYMAN,
        requirements={"stats": {"INT": 15, "MND": 10}},
        stat_bonuses={"INT": 2, "MND": 1},
        exp_bonus=1.1,
        sort_order=21,
    ),
    Job(
        job_id="monk",
        name="修行僧",
        description="精神を極めし者",
        icon="☯️",
        tier=JobTier.JOURNEYMAN,
        requirements={"stats": {"MND": 15, "VIT": 10}},
        stat_bonuses={"MND": 2, "VIT": 1},
        exp_bonus=1.1,
        sort_order=22,
    ),
    
    # Expert tier
    Job(
        job_id="champion",
        name="チャンピオン",
        description="肉体の極致に達した者",
        icon="🏆",
        tier=JobTier.EXPERT,
        requirements={
            "stats": {"STR": 30, "VIT": 25},
            "achievements": ["streak_30"]
        },
        stat_bonuses={"STR": 3, "VIT": 2},
        exp_bonus=1.2,
        sort_order=30,
    ),
    Job(
        job_id="sage",
        name="賢者",
        description="知恵を極めし者",
        icon="🧙",
        tier=JobTier.EXPERT,
        requirements={
            "stats": {"INT": 30, "MND": 25},
            "achievements": ["streak_30"]
        },
        stat_bonuses={"INT": 3, "MND": 2},
        exp_bonus=1.2,
        sort_order=31,
    ),
    
    # Master tier
    Job(
        job_id="hero",
        name="英雄",
        description="すべての能力を高めた伝説の存在",
        icon="🦸",
        tier=JobTier.MASTER,
        requirements={
            "level": 50,
            "stats": {"STR": 20, "INT": 20, "MND": 20, "VIT": 20, "DEX": 20, "CHA": 20}
        },
        stat_bonuses={"STR": 2, "INT": 2, "MND": 2, "VIT": 2, "DEX": 2, "CHA": 2},
        exp_bonus=1.5,
        sort_order=40,
    ),
    
    # Grandmaster tier
    Job(
        job_id="legend",
        name="伝説",
        description="歴史に名を刻む者",
        icon="👑",
        tier=JobTier.GRANDMASTER,
        requirements={
            "level": 99,
            "achievements": ["streak_365"]
        },
        stat_bonuses={"STR": 5, "INT": 5, "MND": 5, "VIT": 5, "DEX": 5, "CHA": 5},
        exp_bonus=2.0,
        sort_order=50,
    ),
]
