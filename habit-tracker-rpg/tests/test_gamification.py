"""Tests for gamification models."""
import pytest
from src.models.gamification import (
    StatType,
    LevelConfig,
    StreakBonus,
    ExpGain,
    get_stat_for_category,
    DEFAULT_LEVEL_CONFIG,
)


class TestLevelConfig:
    """Tests for LevelConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = LevelConfig()
        assert config.base_exp == 100
        assert config.growth_rate == 1.5
        assert config.max_level == 99

    def test_exp_for_level_1(self):
        """Test EXP for level 1 is 0."""
        config = LevelConfig()
        assert config.exp_for_level(1) == 0

    def test_exp_for_level_2(self):
        """Test EXP for level 2 is base_exp."""
        config = LevelConfig()
        assert config.exp_for_level(2) == 100

    def test_exp_for_level_increases(self):
        """Test EXP requirement increases with level."""
        config = LevelConfig()
        exp_2 = config.exp_for_level(2)
        exp_3 = config.exp_for_level(3)
        exp_4 = config.exp_for_level(4)
        
        assert exp_3 > exp_2
        assert exp_4 > exp_3

    def test_level_from_exp_level_1(self):
        """Test level 1 with 0 EXP."""
        config = LevelConfig()
        assert config.level_from_exp(0) == 1
        assert config.level_from_exp(50) == 1
        assert config.level_from_exp(99) == 1

    def test_level_from_exp_level_2(self):
        """Test level 2 with enough EXP."""
        config = LevelConfig()
        assert config.level_from_exp(100) == 2
        assert config.level_from_exp(150) == 2

    def test_exp_to_next_level(self):
        """Test calculating EXP needed for next level."""
        config = LevelConfig()
        
        # At 0 EXP, need 100 to reach level 2
        assert config.exp_to_next_level(0) == 100
        
        # At 50 EXP, need 50 more to reach level 2
        assert config.exp_to_next_level(50) == 50

    def test_max_level_cap(self):
        """Test that level is capped at max_level."""
        config = LevelConfig()
        huge_exp = 10000000000
        assert config.level_from_exp(huge_exp) == config.max_level


class TestStreakBonus:
    """Tests for StreakBonus."""

    def test_default_bonuses(self):
        """Test default bonus values."""
        bonus = StreakBonus()
        assert 3 in bonus.bonuses
        assert 7 in bonus.bonuses
        assert 30 in bonus.bonuses

    def test_no_streak_bonus(self):
        """Test no bonus for 0-2 days."""
        bonus = StreakBonus()
        assert bonus.get_multiplier(0) == 1.0
        assert bonus.get_multiplier(1) == 1.0
        assert bonus.get_multiplier(2) == 1.0

    def test_3_day_streak_bonus(self):
        """Test 3-day streak bonus."""
        bonus = StreakBonus()
        assert bonus.get_multiplier(3) == 1.1
        assert bonus.get_multiplier(5) == 1.1

    def test_7_day_streak_bonus(self):
        """Test 7-day streak bonus."""
        bonus = StreakBonus()
        assert bonus.get_multiplier(7) == 1.25
        assert bonus.get_multiplier(10) == 1.25

    def test_30_day_streak_bonus(self):
        """Test 30-day streak bonus."""
        bonus = StreakBonus()
        assert bonus.get_multiplier(30) == 2.0
        assert bonus.get_multiplier(45) == 2.0


class TestExpGain:
    """Tests for ExpGain."""

    def test_default_base_exp(self):
        """Test default base EXP."""
        gain = ExpGain()
        assert gain.base_exp == 10

    def test_calculate_exp_normal_difficulty(self):
        """Test EXP calculation for normal difficulty."""
        gain = ExpGain()
        exp = gain.calculate_exp(difficulty="normal", streak_days=0)
        assert exp == 10

    def test_calculate_exp_easy_difficulty(self):
        """Test EXP calculation for easy difficulty."""
        gain = ExpGain()
        exp = gain.calculate_exp(difficulty="easy", streak_days=0)
        assert exp == 5

    def test_calculate_exp_hard_difficulty(self):
        """Test EXP calculation for hard difficulty."""
        gain = ExpGain()
        exp = gain.calculate_exp(difficulty="hard", streak_days=0)
        assert exp == 15

    def test_calculate_exp_with_streak(self):
        """Test EXP calculation with streak bonus."""
        gain = ExpGain()
        # 7-day streak gives 1.25x bonus
        exp = gain.calculate_exp(difficulty="normal", streak_days=7)
        assert exp == 12  # 10 * 1.0 * 1.25 = 12.5 -> 12


class TestGetStatForCategory:
    """Tests for get_stat_for_category function."""

    def test_exercise_returns_vitality(self):
        """Test exercise category returns vitality stat."""
        assert get_stat_for_category("exercise") == StatType.VITALITY

    def test_reading_returns_intelligence(self):
        """Test reading category returns intelligence stat."""
        assert get_stat_for_category("reading") == StatType.INTELLIGENCE

    def test_meditation_returns_mental(self):
        """Test meditation category returns mental stat."""
        assert get_stat_for_category("meditation") == StatType.MENTAL

    def test_music_returns_dexterity(self):
        """Test music category returns dexterity stat."""
        assert get_stat_for_category("music") == StatType.DEXTERITY

    def test_communication_returns_charisma(self):
        """Test communication category returns charisma stat."""
        assert get_stat_for_category("communication") == StatType.CHARISMA

    def test_workout_returns_strength(self):
        """Test workout category returns strength stat."""
        assert get_stat_for_category("workout") == StatType.STRENGTH

    def test_unknown_returns_mental(self):
        """Test unknown category defaults to mental stat."""
        assert get_stat_for_category("unknown") == StatType.MENTAL
