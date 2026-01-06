"""Tests for services."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date, datetime


class TestUserService:
    """Tests for UserService."""

    def test_create_user(self):
        """Test creating a new user."""
        from src.services.user_service import UserService
        
        mock_repo = MagicMock()
        mock_repo.get_item.return_value = None  # User doesn't exist
        mock_repo.put_item.return_value = None
        
        service = UserService(mock_repo)
        
        user = service.create_user(
            user_id="test-user-123",
            email="test@example.com",
        )
        
        assert user.user_id == "test-user-123"
        assert user.email == "test@example.com"
        assert user.level == 1
        assert user.total_exp == 0
        mock_repo.put_item.assert_called_once()

    def test_get_user_exists(self, sample_user):
        """Test getting an existing user."""
        from src.services.user_service import UserService
        
        mock_repo = MagicMock()
        mock_repo.get_item.return_value = sample_user
        
        service = UserService(mock_repo)
        
        user = service.get_user("test-user-123")
        
        assert user is not None
        assert user.user_id == "test-user-123"

    def test_get_user_not_exists(self):
        """Test getting a non-existent user."""
        from src.services.user_service import UserService
        
        mock_repo = MagicMock()
        mock_repo.get_item.return_value = None
        
        service = UserService(mock_repo)
        
        user = service.get_user("unknown-user")
        
        assert user is None

    def test_add_experience(self, sample_user):
        """Test adding experience to a user."""
        from src.services.user_service import UserService
        from src.models.gamification import StatType
        
        mock_repo = MagicMock()
        mock_repo.get_item.return_value = sample_user
        mock_repo.update_item.return_value = {**sample_user, "total_exp": 50}
        
        service = UserService(mock_repo)
        
        user = service.add_experience(
            user_id="test-user-123",
            stat_type=StatType.VITALITY,
            exp_amount=50,
        )
        
        assert user is not None


class TestHabitService:
    """Tests for HabitService."""

    def test_create_habit(self):
        """Test creating a new habit."""
        from src.services.habit_service import HabitService
        from src.models.habit import HabitCreate, HabitCategory
        
        mock_repo = MagicMock()
        mock_repo.put_item.return_value = None
        
        service = HabitService(mock_repo)
        
        habit_data = HabitCreate(
            name="Morning Exercise",
            category=HabitCategory.EXERCISE,
        )
        
        habit = service.create_habit(
            user_id="test-user-123",
            habit_data=habit_data,
        )
        
        assert habit.name == "Morning Exercise"
        assert habit.user_id == "test-user-123"
        mock_repo.put_item.assert_called_once()

    def test_list_habits(self, sample_habit):
        """Test listing habits for a user."""
        from src.services.habit_service import HabitService
        
        mock_repo = MagicMock()
        mock_repo.query.return_value = [sample_habit]
        
        service = HabitService(mock_repo)
        
        habits = service.list_habits("test-user-123")
        
        assert len(habits) == 1
        assert habits[0].name == "Morning Exercise"

    def test_get_habit_exists(self, sample_habit):
        """Test getting an existing habit."""
        from src.services.habit_service import HabitService
        
        mock_repo = MagicMock()
        mock_repo.get_item.return_value = sample_habit
        
        service = HabitService(mock_repo)
        
        habit = service.get_habit("test-habit-123", "test-user-123")
        
        assert habit is not None
        assert habit.habit_id == "test-habit-123"

    def test_get_habit_not_found(self):
        """Test getting a non-existent habit."""
        from src.services.habit_service import HabitService
        
        mock_repo = MagicMock()
        mock_repo.get_item.return_value = None
        
        service = HabitService(mock_repo)
        
        habit = service.get_habit("unknown", "test-user-123")
        
        assert habit is None

    def test_delete_habit(self, sample_habit):
        """Test deleting a habit."""
        from src.services.habit_service import HabitService
        
        mock_repo = MagicMock()
        mock_repo.get_item.return_value = sample_habit
        mock_repo.delete_item.return_value = None
        
        service = HabitService(mock_repo)
        
        result = service.delete_habit("test-habit-123", "test-user-123")
        
        assert result is True
        mock_repo.delete_item.assert_called_once()


class TestRecordService:
    """Tests for RecordService."""

    def test_create_record(self, sample_habit):
        """Test creating a habit record."""
        from src.services.record_service import RecordService
        from src.models.record import RecordCreate
        
        mock_repo = MagicMock()
        mock_repo.put_item.return_value = None
        mock_repo.get_item.return_value = sample_habit
        
        service = RecordService(mock_repo)
        
        record_data = RecordCreate(
            habit_id="test-habit-123",
            completed=True,
            note="Great workout!",
        )
        
        record = service.create_record(
            user_id="test-user-123",
            record_data=record_data,
        )
        
        assert record.habit_id == "test-habit-123"
        assert record.completed is True

    def test_list_records_by_date(self, sample_record):
        """Test listing records for a specific date."""
        from src.services.record_service import RecordService
        
        mock_repo = MagicMock()
        mock_repo.query.return_value = [sample_record]
        
        service = RecordService(mock_repo)
        
        records = service.list_records_by_date(
            user_id="test-user-123",
            target_date=date.today(),
        )
        
        assert len(records) == 1


class TestAchievementService:
    """Tests for AchievementService."""

    def test_list_achievements(self):
        """Test listing all achievements."""
        from src.services.achievement_service import AchievementService
        from src.models.achievement import PREDEFINED_ACHIEVEMENTS
        
        mock_repo = MagicMock()
        
        service = AchievementService(mock_repo)
        
        achievements = service.list_all_achievements()
        
        assert len(achievements) == len(PREDEFINED_ACHIEVEMENTS)

    def test_get_user_achievements(self):
        """Test getting user's unlocked achievements."""
        from src.services.achievement_service import AchievementService
        
        mock_repo = MagicMock()
        mock_repo.query.return_value = [
            {
                "user_id": "test-user-123",
                "achievement_id": "first_habit",
                "unlocked_at": datetime.utcnow().isoformat(),
            }
        ]
        
        service = AchievementService(mock_repo)
        
        user_achievements = service.get_user_achievements("test-user-123")
        
        assert len(user_achievements) == 1


class TestJobService:
    """Tests for JobService."""

    def test_list_jobs(self):
        """Test listing all jobs."""
        from src.services.job_service import JobService
        from src.models.job import PREDEFINED_JOBS
        
        mock_repo = MagicMock()
        
        service = JobService(mock_repo)
        
        jobs = service.list_all_jobs()
        
        assert len(jobs) == len(PREDEFINED_JOBS)

    def test_get_user_jobs(self):
        """Test getting user's unlocked jobs."""
        from src.services.job_service import JobService
        
        mock_repo = MagicMock()
        mock_repo.query.return_value = [
            {
                "user_id": "test-user-123",
                "job_id": "beginner",
                "unlocked_at": datetime.utcnow().isoformat(),
                "is_equipped": True,
            }
        ]
        
        service = JobService(mock_repo)
        
        user_jobs = service.get_user_jobs("test-user-123")
        
        assert len(user_jobs) == 1

    def test_equip_job(self):
        """Test equipping a job."""
        from src.services.job_service import JobService
        
        mock_repo = MagicMock()
        mock_repo.query.return_value = [
            {
                "user_id": "test-user-123",
                "job_id": "beginner",
                "unlocked_at": datetime.utcnow().isoformat(),
                "is_equipped": False,
            }
        ]
        mock_repo.update_item.return_value = {
            "user_id": "test-user-123",
            "job_id": "beginner",
            "unlocked_at": datetime.utcnow().isoformat(),
            "is_equipped": True,
        }
        
        service = JobService(mock_repo)
        
        result = service.equip_job("test-user-123", "beginner")
        
        assert result is True
