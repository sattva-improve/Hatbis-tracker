"""Pytest configuration and fixtures."""
import os
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

# Set test environment variables before imports
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "ap-northeast-1"
os.environ["DYNAMODB_ENDPOINT_URL"] = "http://localhost:4566"
os.environ["USERS_TABLE"] = "test-users"
os.environ["HABITS_TABLE"] = "test-habits"
os.environ["RECORDS_TABLE"] = "test-records"
os.environ["USER_ACHIEVEMENTS_TABLE"] = "test-user-achievements"
os.environ["USER_JOBS_TABLE"] = "test-user-jobs"
os.environ["COGNITO_USER_POOL_ID"] = "test-pool-id"
os.environ["COGNITO_CLIENT_ID"] = "test-client-id"


@pytest.fixture
def mock_dynamodb_table():
    """Create a mock DynamoDB table."""
    mock_table = MagicMock()
    mock_table.put_item = MagicMock(return_value={})
    mock_table.get_item = MagicMock(return_value={"Item": {}})
    mock_table.update_item = MagicMock(return_value={"Attributes": {}})
    mock_table.delete_item = MagicMock(return_value={})
    mock_table.query = MagicMock(return_value={"Items": []})
    mock_table.scan = MagicMock(return_value={"Items": []})
    return mock_table


@pytest.fixture
def sample_user():
    """Create a sample user data."""
    return {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "profile": {
            "display_name": "Test User",
            "avatar_url": None,
            "bio": None,
            "timezone": "Asia/Tokyo",
        },
        "stats": {
            "vitality": 1,
            "intelligence": 1,
            "mental": 1,
            "dexterity": 1,
            "charisma": 1,
            "strength": 1,
            "vitality_exp": 0,
            "intelligence_exp": 0,
            "mental_exp": 0,
            "dexterity_exp": 0,
            "charisma_exp": 0,
            "strength_exp": 0,
        },
        "level": 1,
        "total_exp": 0,
        "current_job_id": "beginner",
        "max_streak": 0,
        "current_streak": 0,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_habit():
    """Create a sample habit data."""
    return {
        "habit_id": "test-habit-123",
        "user_id": "test-user-123",
        "name": "Morning Exercise",
        "description": "30 minutes of exercise every morning",
        "icon": "🏃",
        "color": "#4CAF50",
        "category": "exercise",
        "stat_type": "VIT",
        "frequency": {
            "type": "daily",
            "times_per_week": None,
            "specific_days": None,
        },
        "difficulty": "normal",
        "reminder_enabled": True,
        "reminder_time": "07:00:00",
        "current_streak": 5,
        "best_streak": 10,
        "total_completions": 50,
        "is_active": True,
        "is_archived": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "last_completed_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_record():
    """Create a sample habit record data."""
    from datetime import date
    return {
        "record_id": "test-record-123",
        "habit_id": "test-habit-123",
        "user_id": "test-user-123",
        "completed_date": date.today().isoformat(),
        "completed": True,
        "note": "Great workout today!",
        "exp_earned": 15,
        "streak_at_completion": 6,
        "created_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def api_gateway_event():
    """Create a sample API Gateway event."""
    def _create_event(
        method="GET",
        path="/",
        body=None,
        path_params=None,
        query_params=None,
        headers=None,
        user_id=None,
    ):
        event = {
            "httpMethod": method,
            "path": path,
            "body": body,
            "pathParameters": path_params or {},
            "queryStringParameters": query_params or {},
            "headers": headers or {},
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": user_id or "test-user-123",
                    }
                }
            },
        }
        return event
    return _create_event


@pytest.fixture
def lambda_context():
    """Create a mock Lambda context."""
    context = MagicMock()
    context.function_name = "test-function"
    context.memory_limit_in_mb = 256
    context.invoked_function_arn = "arn:aws:lambda:ap-northeast-1:123456789012:function:test-function"
    context.aws_request_id = "test-request-id"
    return context
