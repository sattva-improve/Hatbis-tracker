"""Common utilities for Lambda handlers."""
import json
import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, Optional

import boto3
from jose import jwt, JWTError

# Logger setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
COGNITO_REGION = os.environ.get("COGNITO_REGION", "ap-northeast-1")
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID", "")
DYNAMODB_TABLE_PREFIX = os.environ.get("DYNAMODB_TABLE_PREFIX", "habit-tracker-rpg")


def get_dynamodb_resource():
    """Get DynamoDB resource."""
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL")
    if endpoint_url:
        return boto3.resource("dynamodb", endpoint_url=endpoint_url)
    return boto3.resource("dynamodb")


def get_cognito_client():
    """Get Cognito client."""
    endpoint_url = os.environ.get("COGNITO_ENDPOINT_URL")
    if endpoint_url:
        return boto3.client(
            "cognito-idp",
            endpoint_url=endpoint_url,
            region_name=COGNITO_REGION
        )
    return boto3.client("cognito-idp", region_name=COGNITO_REGION)


def create_response(
    status_code: int,
    body: Any = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create a standardized API Gateway response."""
    response_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    }
    if headers:
        response_headers.update(headers)
    
    response = {
        "statusCode": status_code,
        "headers": response_headers,
    }
    
    if body is not None:
        response["body"] = json.dumps(body, default=str, ensure_ascii=False)
    
    return response


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create an error response."""
    body = {
        "code": code,
        "message": message,
    }
    if details:
        body["details"] = details
    return create_response(status_code, body)


def get_user_id_from_event(event: Dict[str, Any]) -> Optional[str]:
    """Extract user ID from API Gateway event."""
    # Check for Cognito authorizer claims
    request_context = event.get("requestContext", {})
    authorizer = request_context.get("authorizer", {})
    
    # Lambda authorizer
    if "claims" in authorizer:
        return authorizer["claims"].get("sub")
    
    # JWT authorizer
    if "jwt" in authorizer:
        return authorizer["jwt"].get("claims", {}).get("sub")
    
    # Cognito User Pool authorizer
    if "sub" in authorizer:
        return authorizer["sub"]
    
    return None


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse request body from event."""
    body = event.get("body", "{}")
    if body is None:
        return {}
    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}
    return body


def get_path_parameter(event: Dict[str, Any], name: str) -> Optional[str]:
    """Get a path parameter from event."""
    params = event.get("pathParameters") or {}
    return params.get(name)


def get_query_parameter(
    event: Dict[str, Any],
    name: str,
    default: Optional[str] = None
) -> Optional[str]:
    """Get a query string parameter from event."""
    params = event.get("queryStringParameters") or {}
    return params.get(name, default)


def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication."""
    @wraps(func)
    def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        user_id = get_user_id_from_event(event)
        if not user_id:
            return error_response(401, "UNAUTHORIZED", "認証が必要です")
        
        # Add user_id to event for handlers
        event["user_id"] = user_id
        return func(event, context)
    return wrapper


def handle_exceptions(func: Callable) -> Callable:
    """Decorator to handle exceptions."""
    @wraps(func)
    def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        try:
            return func(event, context)
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return error_response(400, "VALIDATION_ERROR", str(e))
        except KeyError as e:
            logger.error(f"Missing key: {e}")
            return error_response(400, "MISSING_FIELD", f"必須フィールドがありません: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return error_response(500, "INTERNAL_ERROR", "内部エラーが発生しました")
    return wrapper
