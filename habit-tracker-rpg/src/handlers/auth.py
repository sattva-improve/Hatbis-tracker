"""Authentication handlers for Cognito."""
import os
import logging
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

from .common import (
    create_response,
    error_response,
    parse_body,
    get_cognito_client,
    handle_exceptions,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID", "")


@handle_exceptions
def sign_up(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle user registration."""
    body = parse_body(event)
    
    email = body.get("email")
    password = body.get("password")
    display_name = body.get("display_name")
    timezone = body.get("timezone", "Asia/Tokyo")
    
    if not email or not password or not display_name:
        return error_response(400, "MISSING_FIELDS", "email, password, display_name は必須です")
    
    cognito = get_cognito_client()
    
    try:
        # Register user in Cognito
        response = cognito.sign_up(
            ClientId=COGNITO_CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "custom:display_name", "Value": display_name},
                {"Name": "custom:timezone", "Value": timezone},
            ],
        )
        
        user_sub = response["UserSub"]
        
        # Auto-confirm for development (remove in production)
        if os.environ.get("AUTO_CONFIRM_USER", "false").lower() == "true":
            cognito.admin_confirm_sign_up(
                UserPoolId=os.environ.get("COGNITO_USER_POOL_ID"),
                Username=email,
            )
        
        # Create user in DynamoDB
        from ..services.user_service import UserService
        user_service = UserService()
        user = user_service.create_user(
            user_id=user_sub,
            email=email,
            display_name=display_name,
            timezone=timezone,
        )
        
        return create_response(201, {
            "message": "ユーザー登録が完了しました",
            "user_id": user_sub,
            "user": user.model_dump(),
        })
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "UsernameExistsException":
            return error_response(409, "USER_EXISTS", "このメールアドレスは既に登録されています")
        elif error_code == "InvalidPasswordException":
            return error_response(400, "INVALID_PASSWORD", "パスワードが要件を満たしていません")
        else:
            logger.error(f"Cognito error: {e}")
            return error_response(500, "COGNITO_ERROR", str(e))


@handle_exceptions
def sign_in(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle user login."""
    body = parse_body(event)
    
    email = body.get("email")
    password = body.get("password")
    
    if not email or not password:
        return error_response(400, "MISSING_FIELDS", "email と password は必須です")
    
    cognito = get_cognito_client()
    
    try:
        response = cognito.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password,
            },
        )
        
        auth_result = response.get("AuthenticationResult", {})
        
        return create_response(200, {
            "access_token": auth_result.get("AccessToken"),
            "refresh_token": auth_result.get("RefreshToken"),
            "expires_in": auth_result.get("ExpiresIn"),
            "token_type": "Bearer",
        })
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ["NotAuthorizedException", "UserNotFoundException"]:
            return error_response(401, "INVALID_CREDENTIALS", "メールアドレスまたはパスワードが間違っています")
        elif error_code == "UserNotConfirmedException":
            return error_response(401, "USER_NOT_CONFIRMED", "メールアドレスの確認が完了していません")
        else:
            logger.error(f"Cognito error: {e}")
            return error_response(500, "COGNITO_ERROR", str(e))


@handle_exceptions
def sign_out(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle user logout."""
    # Get access token from Authorization header
    headers = event.get("headers", {})
    auth_header = headers.get("Authorization") or headers.get("authorization", "")
    
    if not auth_header.startswith("Bearer "):
        return error_response(401, "INVALID_TOKEN", "有効なトークンが必要です")
    
    access_token = auth_header[7:]
    
    cognito = get_cognito_client()
    
    try:
        cognito.global_sign_out(AccessToken=access_token)
        return create_response(204)
        
    except ClientError as e:
        logger.error(f"Cognito error: {e}")
        return error_response(500, "COGNITO_ERROR", "ログアウトに失敗しました")


@handle_exceptions
def refresh_token(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle token refresh."""
    body = parse_body(event)
    
    refresh_token_value = body.get("refresh_token")
    
    if not refresh_token_value:
        return error_response(400, "MISSING_FIELDS", "refresh_token は必須です")
    
    cognito = get_cognito_client()
    
    try:
        response = cognito.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": refresh_token_value,
            },
        )
        
        auth_result = response.get("AuthenticationResult", {})
        
        return create_response(200, {
            "access_token": auth_result.get("AccessToken"),
            "expires_in": auth_result.get("ExpiresIn"),
            "token_type": "Bearer",
        })
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NotAuthorizedException":
            return error_response(401, "INVALID_TOKEN", "リフレッシュトークンが無効です")
        else:
            logger.error(f"Cognito error: {e}")
            return error_response(500, "COGNITO_ERROR", str(e))


@handle_exceptions
def change_password(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle password change."""
    # Get access token from Authorization header
    headers = event.get("headers", {})
    auth_header = headers.get("Authorization") or headers.get("authorization", "")
    
    if not auth_header.startswith("Bearer "):
        return error_response(401, "INVALID_TOKEN", "有効なトークンが必要です")
    
    access_token = auth_header[7:]
    
    body = parse_body(event)
    current_password = body.get("current_password")
    new_password = body.get("new_password")
    
    if not current_password or not new_password:
        return error_response(400, "MISSING_FIELDS", "current_password と new_password は必須です")
    
    cognito = get_cognito_client()
    
    try:
        cognito.change_password(
            PreviousPassword=current_password,
            ProposedPassword=new_password,
            AccessToken=access_token,
        )
        
        return create_response(204)
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NotAuthorizedException":
            return error_response(401, "INVALID_PASSWORD", "現在のパスワードが間違っています")
        elif error_code == "InvalidPasswordException":
            return error_response(400, "INVALID_NEW_PASSWORD", "新しいパスワードが要件を満たしていません")
        else:
            logger.error(f"Cognito error: {e}")
            return error_response(500, "COGNITO_ERROR", str(e))
