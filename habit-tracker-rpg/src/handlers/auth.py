"""Authentication handlers for Cognito with SSO support."""
import os
import logging
import urllib.parse
from typing import Any, Dict

import boto3
import requests
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
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID", "")
COGNITO_DOMAIN = os.environ.get("COGNITO_DOMAIN", "")
COGNITO_REGION = os.environ.get("COGNITO_REGION", "ap-northeast-1")


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


# =============================================================================
# SSO (Social Sign-In) Handlers
# =============================================================================

@handle_exceptions
def get_sso_login_url(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get SSO login URLs for supported providers.
    
    Returns URLs for Google, Apple sign-in through Cognito Hosted UI.
    """
    query_params = event.get("queryStringParameters") or {}
    redirect_uri = query_params.get("redirect_uri", "http://localhost:3000/auth/callback")
    
    # Validate redirect_uri (should be in allowed list)
    allowed_redirect_uris = [
        "http://localhost:3000/auth/callback",
        # Add production URLs here
    ]
    
    if redirect_uri not in allowed_redirect_uris:
        redirect_uri = allowed_redirect_uris[0]
    
    base_url = f"https://{COGNITO_DOMAIN}.auth.{COGNITO_REGION}.amazoncognito.com"
    
    # Build OAuth URLs
    common_params = {
        "client_id": COGNITO_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "email openid profile",
    }
    
    google_params = {**common_params, "identity_provider": "Google"}
    apple_params = {**common_params, "identity_provider": "SignInWithApple"}
    
    return create_response(200, {
        "providers": {
            "google": {
                "name": "Google",
                "icon": "🔵",
                "login_url": f"{base_url}/oauth2/authorize?{urllib.parse.urlencode(google_params)}",
            },
            "apple": {
                "name": "Apple",
                "icon": "🍎",
                "login_url": f"{base_url}/oauth2/authorize?{urllib.parse.urlencode(apple_params)}",
            },
        },
        "cognito_hosted_ui": f"{base_url}/login?{urllib.parse.urlencode(common_params)}",
    })


@handle_exceptions
def sso_callback(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle OAuth callback from Cognito Hosted UI.
    
    Exchanges authorization code for tokens and creates/updates user.
    """
    query_params = event.get("queryStringParameters") or {}
    code = query_params.get("code")
    error = query_params.get("error")
    error_description = query_params.get("error_description", "Unknown error")
    
    if error:
        logger.error(f"SSO error: {error} - {error_description}")
        return error_response(400, "SSO_ERROR", error_description)
    
    if not code:
        return error_response(400, "MISSING_CODE", "Authorization code is required")
    
    # Get redirect_uri from state or use default
    redirect_uri = query_params.get("redirect_uri", "http://localhost:3000/auth/callback")
    
    # Exchange code for tokens
    token_url = f"https://{COGNITO_DOMAIN}.auth.{COGNITO_REGION}.amazoncognito.com/oauth2/token"
    
    try:
        token_response = requests.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": COGNITO_CLIENT_ID,
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            return error_response(400, "TOKEN_EXCHANGE_FAILED", "Failed to exchange authorization code")
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        id_token = tokens.get("id_token")
        refresh_token = tokens.get("refresh_token")
        
        # Get user info from Cognito
        cognito = get_cognito_client()
        user_info = cognito.get_user(AccessToken=access_token)
        
        user_sub = user_info.get("Username")
        user_attributes = {
            attr["Name"]: attr["Value"] 
            for attr in user_info.get("UserAttributes", [])
        }
        
        email = user_attributes.get("email", "")
        display_name = user_attributes.get("custom:display_name") or user_attributes.get("name", email.split("@")[0])
        timezone = user_attributes.get("custom:timezone", "Asia/Tokyo")
        auth_provider = user_attributes.get("identities", "cognito")
        
        # Parse identities to get provider
        if auth_provider != "cognito":
            try:
                import json
                identities = json.loads(auth_provider)
                if identities:
                    auth_provider = identities[0].get("providerName", "cognito")
            except:
                auth_provider = "external"
        
        # Create or update user in DynamoDB
        from ..services.user_service import UserService
        user_service = UserService()
        
        try:
            user = user_service.get_user(user_sub)
            # Update last login
            user_service.update_user(user_sub, {"last_login_at": None})  # Will use current time
        except:
            # Create new user
            user = user_service.create_user(
                user_id=user_sub,
                email=email,
                display_name=display_name,
                timezone=timezone,
            )
        
        return create_response(200, {
            "access_token": access_token,
            "id_token": id_token,
            "refresh_token": refresh_token,
            "expires_in": tokens.get("expires_in", 3600),
            "token_type": "Bearer",
            "user": {
                "user_id": user_sub,
                "email": email,
                "display_name": display_name,
                "auth_provider": auth_provider,
            },
        })
        
    except requests.RequestException as e:
        logger.error(f"Token exchange request failed: {e}")
        return error_response(500, "TOKEN_EXCHANGE_ERROR", "Failed to exchange authorization code")
    except ClientError as e:
        logger.error(f"Cognito error: {e}")
        return error_response(500, "COGNITO_ERROR", str(e))


@handle_exceptions
def get_user_info(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get current user info from access token.
    
    Used to validate token and get user details.
    """
    headers = event.get("headers", {})
    auth_header = headers.get("Authorization") or headers.get("authorization", "")
    
    if not auth_header.startswith("Bearer "):
        return error_response(401, "INVALID_TOKEN", "有効なトークンが必要です")
    
    access_token = auth_header[7:]
    
    cognito = get_cognito_client()
    
    try:
        user_info = cognito.get_user(AccessToken=access_token)
        
        user_attributes = {
            attr["Name"]: attr["Value"] 
            for attr in user_info.get("UserAttributes", [])
        }
        
        # Get user from DynamoDB for additional info
        from ..services.user_service import UserService
        user_service = UserService()
        
        user_sub = user_info.get("Username")
        
        try:
            user = user_service.get_user(user_sub)
            user_data = user.model_dump()
        except:
            user_data = None
        
        return create_response(200, {
            "user_id": user_sub,
            "email": user_attributes.get("email"),
            "display_name": user_attributes.get("custom:display_name"),
            "timezone": user_attributes.get("custom:timezone", "Asia/Tokyo"),
            "email_verified": user_attributes.get("email_verified") == "true",
            "user_data": user_data,
        })
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NotAuthorizedException":
            return error_response(401, "TOKEN_EXPIRED", "トークンが期限切れです")
        else:
            logger.error(f"Cognito error: {e}")
            return error_response(500, "COGNITO_ERROR", str(e))
