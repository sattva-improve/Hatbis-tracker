"""Tests for habit models."""
import pytest
from datetime import time
from src.models.habit import (
    Habit,
    HabitCategory,
    HabitDifficulty,
    HabitFrequency,
    FrequencyType,
    HabitCreate,
)
from src.models.gamification import StatType


class TestHabitFrequency:
    """Tests for HabitFrequency."""

    def test_daily_frequency_is_due_every_day(self):
        """Test daily frequency is due every day."""
        freq = HabitFrequency(type=FrequencyType.DAILY)
        
        for day in range(7):
            assert freq.is_due_on_day(day) is True

    def test_specific_days_frequency(self):
        """Test specific days frequency."""
        # Monday (0), Wednesday (2), Friday (4)
        freq = HabitFrequency(
            type=FrequencyType.SPECIFIC_DAYS,
            specific_days=[0, 2, 4],
        )
        
        assert freq.is_due_on_day(0) is True  # Monday
        assert freq.is_due_on_day(1) is False  # Tuesday
        assert freq.is_due_on_day(2) is True  # Wednesday
        assert freq.is_due_on_day(3) is False  # Thursday
        assert freq.is_due_on_day(4) is True  # Friday
        assert freq.is_due_on_day(5) is False  # Saturday
        assert freq.is_due_on_day(6) is False  # Sunday

    def test_weekly_frequency_is_due_any_day(self):
        """Test weekly frequency allows any day."""
        freq = HabitFrequency(
            type=FrequencyType.WEEKLY,
            times_per_week=3,
        )
        
        for day in range(7):
            assert freq.is_due_on_day(day) is True


class TestHabitCategory:
    """Tests for HabitCategory enum."""

    def test_all_categories_exist(self):
        """Test all expected categories exist."""
        categories = [
            "exercise", "sleep", "health",  # VIT
            "reading", "study", "learning",  # INT
            "meditation", "journaling", "gratitude", "mindfulness",  # MND
            "music", "art", "craft", "hobby",  # DEX
            "communication", "social", "grooming",  # CHA
            "workout", "sports", "fitness",  # STR
            "other",
        ]
        
        for category in categories:
            assert HabitCategory(category) is not None


class TestHabit:
    """Tests for Habit model."""

    def test_create_habit_with_defaults(self, sample_habit):
        """Test creating a habit with sample data."""
        habit = Habit(**sample_habit)
        
        assert habit.habit_id == "test-habit-123"
        assert habit.name == "Morning Exercise"
        assert habit.category == HabitCategory.EXERCISE
        assert habit.stat_type == StatType.VITALITY
        assert habit.is_active is True

    def test_habit_serialization(self, sample_habit):
        """Test habit can be serialized to dict."""
        habit = Habit(**sample_habit)
        data = habit.model_dump()
        
        assert "habit_id" in data
        assert "name" in data
        assert "category" in data


class TestHabitCreate:
    """Tests for HabitCreate model."""

    def test_create_with_minimal_fields(self):
        """Test creating HabitCreate with only required fields."""
        create_data = HabitCreate(name="Test Habit")
        
        assert create_data.name == "Test Habit"
        assert create_data.icon == "📝"
        assert create_data.color == "#4CAF50"
        assert create_data.category == HabitCategory.OTHER

    def test_create_with_all_fields(self):
        """Test creating HabitCreate with all fields."""
        create_data = HabitCreate(
            name="Morning Jog",
            description="30 minutes jog every morning",
            icon="🏃",
            color="#FF5722",
            category=HabitCategory.EXERCISE,
            difficulty=HabitDifficulty.HARD,
            reminder_enabled=True,
            reminder_time=time(7, 0),
        )
        
        assert create_data.name == "Morning Jog"
        assert create_data.difficulty == HabitDifficulty.HARD
        assert create_data.reminder_enabled is True
