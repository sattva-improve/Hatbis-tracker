"""Tests for Lambda handlers."""
import json
import pytest
from unittest.mock import MagicMock, patch


class TestCommonHandlers:
    """Tests for common handler utilities."""

    def test_create_response(self):
        """Test creating a response."""
        from src.handlers.common import create_response
        
        response = create_response(200, {"message": "success"})
        
        assert response["statusCode"] == 200
        assert "body" in response
        assert "application/json" in response["headers"]["Content-Type"]
        
        body = json.loads(response["body"])
        assert body["message"] == "success"

    def test_error_response(self):
        """Test creating an error response."""
        from src.handlers.common import error_response
        
        response = error_response(400, "VALIDATION_ERROR", "Invalid input")
        
        assert response["statusCode"] == 400
        
        body = json.loads(response["body"])
        assert body["code"] == "VALIDATION_ERROR"
        assert body["message"] == "Invalid input"

    def test_parse_body_json(self):
        """Test parsing JSON body."""
        from src.handlers.common import parse_body
        
        event = {"body": '{"name": "test"}'}
        body = parse_body(event)
        
        assert body["name"] == "test"

    def test_parse_body_empty(self):
        """Test parsing empty body."""
        from src.handlers.common import parse_body
        
        event = {"body": None}
        body = parse_body(event)
        
        assert body == {}

    def test_get_user_id_from_event(self):
        """Test extracting user ID from event."""
        from src.handlers.common import get_user_id_from_event
        
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "user-123"
                    }
                }
            }
        }
        
        user_id = get_user_id_from_event(event)
        assert user_id == "user-123"

    def test_get_path_parameter(self):
        """Test getting path parameter."""
        from src.handlers.common import get_path_parameter
        
        event = {"pathParameters": {"habitId": "habit-123"}}
        
        habit_id = get_path_parameter(event, "habitId")
        assert habit_id == "habit-123"

    def test_get_query_parameter(self):
        """Test getting query parameter."""
        from src.handlers.common import get_query_parameter
        
        event = {"queryStringParameters": {"category": "exercise"}}
        
        category = get_query_parameter(event, "category")
        assert category == "exercise"

    def test_get_query_parameter_with_default(self):
        """Test getting query parameter with default value."""
        from src.handlers.common import get_query_parameter
        
        event = {"queryStringParameters": {}}
        
        category = get_query_parameter(event, "category", "other")
        assert category == "other"


class TestUserHandlers:
    """Tests for user handlers."""

    @patch("src.handlers.users.UserService")
    def test_get_my_profile_success(self, mock_user_service, api_gateway_event, lambda_context, sample_user):
        """Test getting user profile successfully."""
        from src.handlers.users import get_my_profile
        from src.models.user import User
        
        mock_service_instance = MagicMock()
        mock_service_instance.get_user.return_value = User(**sample_user)
        mock_user_service.return_value = mock_service_instance
        
        event = api_gateway_event(method="GET", path="/users/me", user_id="test-user-123")
        
        response = get_my_profile(event, lambda_context)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["user_id"] == "test-user-123"

    @patch("src.handlers.users.UserService")
    def test_get_my_profile_not_found(self, mock_user_service, api_gateway_event, lambda_context):
        """Test getting user profile when not found."""
        from src.handlers.users import get_my_profile
        
        mock_service_instance = MagicMock()
        mock_service_instance.get_user.return_value = None
        mock_user_service.return_value = mock_service_instance
        
        event = api_gateway_event(method="GET", path="/users/me", user_id="unknown-user")
        
        response = get_my_profile(event, lambda_context)
        
        assert response["statusCode"] == 404


class TestHabitHandlers:
    """Tests for habit handlers."""

    @patch("src.handlers.habits.HabitService")
    def test_list_habits_success(self, mock_habit_service, api_gateway_event, lambda_context, sample_habit):
        """Test listing habits successfully."""
        from src.handlers.habits import list_habits
        from src.models.habit import Habit
        
        mock_service_instance = MagicMock()
        mock_service_instance.list_habits.return_value = [Habit(**sample_habit)]
        mock_habit_service.return_value = mock_service_instance
        
        event = api_gateway_event(method="GET", path="/habits", user_id="test-user-123")
        
        response = list_habits(event, lambda_context)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "habits" in body
        assert len(body["habits"]) == 1

    @patch("src.handlers.habits.HabitService")
    def test_create_habit_success(self, mock_habit_service, api_gateway_event, lambda_context, sample_habit):
        """Test creating a habit successfully."""
        from src.handlers.habits import create_habit
        from src.models.habit import Habit
        
        mock_service_instance = MagicMock()
        mock_service_instance.create_habit.return_value = Habit(**sample_habit)
        mock_habit_service.return_value = mock_service_instance
        
        event = api_gateway_event(
            method="POST",
            path="/habits",
            body=json.dumps({"name": "Morning Exercise"}),
            user_id="test-user-123",
        )
        
        response = create_habit(event, lambda_context)
        
        assert response["statusCode"] == 201

    @patch("src.handlers.habits.HabitService")
    def test_create_habit_missing_name(self, mock_habit_service, api_gateway_event, lambda_context):
        """Test creating a habit without name fails."""
        from src.handlers.habits import create_habit
        
        event = api_gateway_event(
            method="POST",
            path="/habits",
            body=json.dumps({}),
            user_id="test-user-123",
        )
        
        response = create_habit(event, lambda_context)
        
        assert response["statusCode"] == 400

    @patch("src.handlers.habits.HabitService")
    def test_get_habit_success(self, mock_habit_service, api_gateway_event, lambda_context, sample_habit):
        """Test getting a habit successfully."""
        from src.handlers.habits import get_habit
        from src.models.habit import Habit
        
        mock_service_instance = MagicMock()
        mock_service_instance.get_habit.return_value = Habit(**sample_habit)
        mock_habit_service.return_value = mock_service_instance
        
        event = api_gateway_event(
            method="GET",
            path="/habits/test-habit-123",
            path_params={"habitId": "test-habit-123"},
            user_id="test-user-123",
        )
        
        response = get_habit(event, lambda_context)
        
        assert response["statusCode"] == 200

    @patch("src.handlers.habits.HabitService")
    def test_get_habit_not_found(self, mock_habit_service, api_gateway_event, lambda_context):
        """Test getting a habit that doesn't exist."""
        from src.handlers.habits import get_habit
        
        mock_service_instance = MagicMock()
        mock_service_instance.get_habit.return_value = None
        mock_habit_service.return_value = mock_service_instance
        
        event = api_gateway_event(
            method="GET",
            path="/habits/unknown",
            path_params={"habitId": "unknown"},
            user_id="test-user-123",
        )
        
        response = get_habit(event, lambda_context)
        
        assert response["statusCode"] == 404
