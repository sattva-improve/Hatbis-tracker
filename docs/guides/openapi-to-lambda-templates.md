# OpenAPI→Lambda テンプレートガイド

> **ドキュメントバージョン**: 1.1.0  
> **最終更新日**: 2025-12-30  
> **ステータス**: Active

このドキュメントでは、OpenAPI仕様からAWS Lambda関数を実装する際に使用するコードテンプレートを提供します。

> **認証方式**: Amazon Cognitoを使用したJWT認証

## 目次

1. [テンプレート概要](#テンプレート概要)
2. [Pydanticモデル](#pydanticモデル)
3. [Lambdaハンドラー](#lambdaハンドラー)
4. [DynamoDBリポジトリ](#dynamodbリポジトリ)
5. [認証・認可（Amazon Cognito）](#認証認可amazon-cognito)
6. [エラーハンドリング](#エラーハンドリング)
7. [ユーティリティ](#ユーティリティ)
8. [テスト](#テスト)
9. [関連ドキュメント](#関連ドキュメント)

---

## テンプレート概要

### テンプレートファイル構成

```
templates/
├── models/
│   ├── base_model.py        # 基本モデル
│   ├── request_model.py     # リクエストモデル
│   └── response_model.py    # レスポンスモデル
├── handlers/
│   ├── base_handler.py      # 基本ハンドラー
│   ├── crud_handler.py      # CRUDハンドラー
│   └── auth_handler.py      # 認証ハンドラー
├── repositories/
│   ├── base_repository.py   # 基本リポジトリ
│   └── dynamodb_repository.py
├── auth/
│   ├── cognito_helper.py    # Cognito操作ヘルパー
│   └── user_context.py      # ユーザーコンテキスト
├── shared/
│   ├── exceptions.py        # カスタム例外
│   ├── responses.py         # レスポンスヘルパー
│   └── pagination.py        # ページネーション
└── tests/
    ├── conftest.py          # Pytestフィクスチャ
    └── test_handler.py      # ハンドラーテスト
```

---

## Pydanticモデル

### 基本モデル（base_model.py）

```python
"""基本Pydanticモデル"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import ulid


class BaseEntity(BaseModel):
    """全エンティティの基底クラス"""
    
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )
    
    id: str = Field(default_factory=lambda: str(ulid.new()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dynamodb_item(self) -> dict:
        """DynamoDB用のアイテムに変換"""
        return {
            k: self._convert_value(v)
            for k, v in self.model_dump().items()
            if v is not None
        }
    
    @staticmethod
    def _convert_value(value):
        """値をDynamoDB用に変換"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> "BaseEntity":
        """DynamoDBアイテムからエンティティを生成"""
        return cls(**item)
```

### リクエストモデル（request_model.py）

```python
"""リクエストPydanticモデル"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class CreateProjectRequest(BaseModel):
    """プロジェクト作成リクエスト"""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="プロジェクト名"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="プロジェクト説明"
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """名前のバリデーション"""
        if not v.strip():
            raise ValueError("名前は必須です")
        return v.strip()


class UpdateProjectRequest(BaseModel):
    """プロジェクト更新リクエスト"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CreateTaskRequest(BaseModel):
    """タスク作成リクエスト"""
    
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: str = Field(default="medium")
    due_date: Optional[str] = None
    assignee_id: Optional[str] = None
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """優先度のバリデーション"""
        allowed = ["low", "medium", "high", "urgent"]
        if v not in allowed:
            raise ValueError(f"優先度は {allowed} のいずれかである必要があります")
        return v


class PaginationParams(BaseModel):
    """ページネーションパラメータ"""
    
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    cursor: Optional[str] = None
```

### レスポンスモデル（response_model.py）

```python
"""レスポンスPydanticモデル"""
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar("T")


class PaginationMeta(BaseModel):
    """ページネーションメタ情報"""
    
    page: int
    per_page: int
    total_count: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_cursor: Optional[str] = None


class ApiResponse(BaseModel, Generic[T]):
    """標準APIレスポンス"""
    
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    errors: Optional[List[dict]] = None
    pagination: Optional[PaginationMeta] = None


class ProjectResponse(BaseModel):
    """プロジェクトレスポンス"""
    
    id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    task_count: int = 0
    status: str
    created_at: datetime
    updated_at: datetime


class TaskResponse(BaseModel):
    """タスクレスポンス"""
    
    id: str
    project_id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assignee_id: Optional[str] = None
    due_date: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ErrorResponse(BaseModel):
    """エラーレスポンス"""
    
    success: bool = False
    error: dict = Field(
        ...,
        example={
            "code": "VALIDATION_ERROR",
            "message": "入力データが不正です",
            "details": []
        }
    )
```

---

## Lambdaハンドラー

### 基本ハンドラー（base_handler.py）

```python
"""基本Lambdaハンドラー"""
import json
import logging
from typing import Any, Callable
from functools import wraps
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from shared.exceptions import AppException, NotFoundError, ValidationError as AppValidationError
from shared.responses import success_response, error_response


logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


def handle_errors(func: Callable) -> Callable:
    """エラーハンドリングデコレータ"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundError as e:
            logger.warning(f"Not found: {e}")
            return error_response(404, "NOT_FOUND", str(e))
        except AppValidationError as e:
            logger.warning(f"Validation error: {e}")
            return error_response(400, "VALIDATION_ERROR", str(e), e.details)
        except ValidationError as e:
            logger.warning(f"Pydantic validation error: {e}")
            details = [
                {"field": ".".join(map(str, err["loc"])), "message": err["msg"]}
                for err in e.errors()
            ]
            return error_response(400, "VALIDATION_ERROR", "入力データが不正です", details)
        except AppException as e:
            logger.error(f"Application error: {e}")
            return error_response(e.status_code, e.code, str(e))
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return error_response(500, "INTERNAL_ERROR", "サーバーエラーが発生しました")
    
    return wrapper


def get_user_from_context(event: dict) -> dict:
    """認証コンテキストからユーザー情報を取得"""
    
    request_context = event.get("requestContext", {})
    authorizer = request_context.get("authorizer", {})
    
    return {
        "user_id": authorizer.get("user_id"),
        "email": authorizer.get("email"),
        "role": authorizer.get("role", "user"),
    }


def parse_body(event: dict) -> dict:
    """リクエストボディをパース"""
    
    body = event.get("body", "{}")
    if isinstance(body, str):
        return json.loads(body) if body else {}
    return body or {}


def get_path_param(event: dict, name: str) -> str:
    """パスパラメータを取得"""
    
    return event.get("pathParameters", {}).get(name)


def get_query_params(event: dict) -> dict:
    """クエリパラメータを取得"""
    
    return event.get("queryStringParameters") or {}
```

### CRUDハンドラー（crud_handler.py）

```python
"""CRUDハンドラーテンプレート"""
import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from handlers.base_handler import (
    handle_errors,
    get_user_from_context,
    parse_body,
    get_path_param,
    get_query_params,
)
from models.request_model import (
    CreateProjectRequest,
    UpdateProjectRequest,
    PaginationParams,
)
from models.response_model import ProjectResponse, ApiResponse
from repositories.project_repository import ProjectRepository
from shared.responses import success_response
from shared.pagination import paginate


logger = Logger()
tracer = Tracer()
repository = ProjectRepository()


@tracer.capture_lambda_handler
@logger.inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """メインハンドラー"""
    
    http_method = event.get("httpMethod", "")
    path = event.get("path", "")
    
    # ルーティング
    if http_method == "GET" and path.endswith("/projects"):
        return list_projects(event)
    elif http_method == "POST" and path.endswith("/projects"):
        return create_project(event)
    elif http_method == "GET" and "/projects/" in path:
        return get_project(event)
    elif http_method == "PUT" and "/projects/" in path:
        return update_project(event)
    elif http_method == "DELETE" and "/projects/" in path:
        return delete_project(event)
    
    return {
        "statusCode": 404,
        "body": json.dumps({"error": "Not Found"})
    }


@handle_errors
def list_projects(event: dict) -> dict:
    """プロジェクト一覧取得"""
    
    user = get_user_from_context(event)
    params = get_query_params(event)
    
    pagination = PaginationParams(
        page=int(params.get("page", 1)),
        per_page=int(params.get("per_page", 20)),
        cursor=params.get("cursor"),
    )
    
    projects, total_count, next_cursor = repository.list_by_user(
        user_id=user["user_id"],
        pagination=pagination,
    )
    
    items = [ProjectResponse(**p.model_dump()) for p in projects]
    
    return success_response(
        data=items,
        pagination=paginate(
            items=items,
            total_count=total_count,
            page=pagination.page,
            per_page=pagination.per_page,
            next_cursor=next_cursor,
        )
    )


@handle_errors
def create_project(event: dict) -> dict:
    """プロジェクト作成"""
    
    user = get_user_from_context(event)
    body = parse_body(event)
    
    request = CreateProjectRequest(**body)
    
    project = repository.create(
        name=request.name,
        description=request.description,
        owner_id=user["user_id"],
    )
    
    return success_response(
        data=ProjectResponse(**project.model_dump()),
        status_code=201,
        message="プロジェクトを作成しました"
    )


@handle_errors
def get_project(event: dict) -> dict:
    """プロジェクト詳細取得"""
    
    project_id = get_path_param(event, "projectId")
    user = get_user_from_context(event)
    
    project = repository.get_by_id(project_id)
    
    # アクセス権チェック
    if project.owner_id != user["user_id"]:
        from shared.exceptions import ForbiddenError
        raise ForbiddenError("このプロジェクトへのアクセス権がありません")
    
    return success_response(data=ProjectResponse(**project.model_dump()))


@handle_errors
def update_project(event: dict) -> dict:
    """プロジェクト更新"""
    
    project_id = get_path_param(event, "projectId")
    user = get_user_from_context(event)
    body = parse_body(event)
    
    request = UpdateProjectRequest(**body)
    
    project = repository.update(
        project_id=project_id,
        user_id=user["user_id"],
        **request.model_dump(exclude_unset=True),
    )
    
    return success_response(
        data=ProjectResponse(**project.model_dump()),
        message="プロジェクトを更新しました"
    )


@handle_errors
def delete_project(event: dict) -> dict:
    """プロジェクト削除"""
    
    project_id = get_path_param(event, "projectId")
    user = get_user_from_context(event)
    
    repository.delete(project_id, user["user_id"])
    
    return success_response(message="プロジェクトを削除しました")
```

---

## DynamoDBリポジトリ

### 基本リポジトリ（base_repository.py）

```python
"""基本リポジトリ"""
import os
from typing import Generic, TypeVar, Optional, List, Tuple, Any
from abc import ABC, abstractmethod
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from shared.exceptions import NotFoundError, DatabaseError


T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """リポジトリ基底クラス"""
    
    def __init__(self):
        self.table_name = os.environ.get("TABLE_NAME")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)
    
    @abstractmethod
    def _get_pk(self, entity_id: str) -> str:
        """プライマリキーを取得"""
        pass
    
    @abstractmethod
    def _get_sk(self, entity_id: str) -> str:
        """ソートキーを取得"""
        pass
    
    @abstractmethod
    def _to_entity(self, item: dict) -> T:
        """DynamoDBアイテムをエンティティに変換"""
        pass
    
    def get_by_id(self, entity_id: str) -> T:
        """IDでエンティティを取得"""
        
        try:
            response = self.table.get_item(
                Key={
                    "PK": self._get_pk(entity_id),
                    "SK": self._get_sk(entity_id),
                }
            )
        except ClientError as e:
            raise DatabaseError(f"データベースエラー: {e}")
        
        item = response.get("Item")
        if not item:
            raise NotFoundError(f"ID {entity_id} のアイテムが見つかりません")
        
        return self._to_entity(item)
    
    def put(self, entity: T) -> T:
        """エンティティを保存"""
        
        item = entity.to_dynamodb_item()
        item["PK"] = self._get_pk(entity.id)
        item["SK"] = self._get_sk(entity.id)
        
        try:
            self.table.put_item(Item=item)
        except ClientError as e:
            raise DatabaseError(f"保存エラー: {e}")
        
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """エンティティを削除"""
        
        try:
            self.table.delete_item(
                Key={
                    "PK": self._get_pk(entity_id),
                    "SK": self._get_sk(entity_id),
                }
            )
            return True
        except ClientError as e:
            raise DatabaseError(f"削除エラー: {e}")
    
    def query_by_pk(
        self,
        pk: str,
        sk_begins_with: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None,
    ) -> Tuple[List[dict], Optional[str]]:
        """PKでクエリ"""
        
        params = {
            "KeyConditionExpression": Key("PK").eq(pk),
            "Limit": limit,
        }
        
        if sk_begins_with:
            params["KeyConditionExpression"] &= Key("SK").begins_with(sk_begins_with)
        
        if cursor:
            import base64
            import json
            params["ExclusiveStartKey"] = json.loads(
                base64.b64decode(cursor).decode()
            )
        
        try:
            response = self.table.query(**params)
        except ClientError as e:
            raise DatabaseError(f"クエリエラー: {e}")
        
        items = response.get("Items", [])
        
        # 次のカーソル
        next_cursor = None
        if "LastEvaluatedKey" in response:
            import base64
            import json
            next_cursor = base64.b64encode(
                json.dumps(response["LastEvaluatedKey"]).encode()
            ).decode()
        
        return items, next_cursor
```

### DynamoDBリポジトリ実装例

```python
"""プロジェクトリポジトリ"""
from datetime import datetime
from typing import List, Tuple, Optional

from repositories.base_repository import BaseRepository
from models.project_model import Project
from models.request_model import PaginationParams
from shared.exceptions import NotFoundError, ForbiddenError


class ProjectRepository(BaseRepository[Project]):
    """プロジェクトリポジトリ"""
    
    def _get_pk(self, entity_id: str) -> str:
        return f"PROJECT#{entity_id}"
    
    def _get_sk(self, entity_id: str) -> str:
        return f"PROJECT#{entity_id}"
    
    def _get_user_pk(self, user_id: str) -> str:
        return f"USER#{user_id}"
    
    def _to_entity(self, item: dict) -> Project:
        return Project(
            id=item.get("id"),
            name=item.get("name"),
            description=item.get("description"),
            owner_id=item.get("owner_id"),
            status=item.get("status", "active"),
            task_count=item.get("task_count", 0),
            created_at=item.get("created_at"),
            updated_at=item.get("updated_at"),
        )
    
    def create(
        self,
        name: str,
        owner_id: str,
        description: Optional[str] = None,
    ) -> Project:
        """プロジェクトを作成"""
        
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
            status="active",
        )
        
        # プロジェクトアイテム
        item = project.to_dynamodb_item()
        item["PK"] = self._get_pk(project.id)
        item["SK"] = self._get_sk(project.id)
        # GSI1: ユーザーのプロジェクト一覧用
        item["GSI1PK"] = self._get_user_pk(owner_id)
        item["GSI1SK"] = f"PROJECT#{project.created_at.isoformat()}"
        
        self.table.put_item(Item=item)
        
        return project
    
    def list_by_user(
        self,
        user_id: str,
        pagination: PaginationParams,
    ) -> Tuple[List[Project], int, Optional[str]]:
        """ユーザーのプロジェクト一覧を取得"""
        
        params = {
            "IndexName": "GSI1",
            "KeyConditionExpression": Key("GSI1PK").eq(self._get_user_pk(user_id)),
            "ScanIndexForward": False,  # 降順（新しい順）
            "Limit": pagination.per_page,
        }
        
        if pagination.cursor:
            import base64
            import json
            params["ExclusiveStartKey"] = json.loads(
                base64.b64decode(pagination.cursor).decode()
            )
        
        response = self.table.query(**params)
        
        items = response.get("Items", [])
        projects = [self._to_entity(item) for item in items]
        
        # 次のカーソル
        next_cursor = None
        if "LastEvaluatedKey" in response:
            import base64
            import json
            next_cursor = base64.b64encode(
                json.dumps(response["LastEvaluatedKey"]).encode()
            ).decode()
        
        # 総数取得（オプション）
        count_response = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(self._get_user_pk(user_id)),
            Select="COUNT",
        )
        total_count = count_response.get("Count", 0)
        
        return projects, total_count, next_cursor
    
    def update(
        self,
        project_id: str,
        user_id: str,
        **kwargs,
    ) -> Project:
        """プロジェクトを更新"""
        
        project = self.get_by_id(project_id)
        
        # アクセス権チェック
        if project.owner_id != user_id:
            raise ForbiddenError("このプロジェクトの編集権限がありません")
        
        # 更新
        update_expressions = []
        expression_values = {}
        
        for key, value in kwargs.items():
            if value is not None:
                update_expressions.append(f"{key} = :{key}")
                expression_values[f":{key}"] = value
        
        # updated_at を更新
        update_expressions.append("updated_at = :updated_at")
        expression_values[":updated_at"] = datetime.utcnow().isoformat()
        
        self.table.update_item(
            Key={
                "PK": self._get_pk(project_id),
                "SK": self._get_sk(project_id),
            },
            UpdateExpression="SET " + ", ".join(update_expressions),
            ExpressionAttributeValues=expression_values,
        )
        
        return self.get_by_id(project_id)
    
    def delete(self, project_id: str, user_id: str) -> bool:
        """プロジェクトを削除"""
        
        project = self.get_by_id(project_id)
        
        if project.owner_id != user_id:
            raise ForbiddenError("このプロジェクトの削除権限がありません")
        
        return super().delete(project_id)
```

---

## 認証・認可（Amazon Cognito）

> **Note**: 認証にはAmazon Cognitoを使用します。API Gateway の Cognito Authorizer により、トークン検証が自動的に行われます。

### アーキテクチャ

```mermaid
flowchart LR
    subgraph Client["クライアント"]
        App[アプリケーション]
    end
    
    subgraph AWS["AWS"]
        Cognito[Amazon Cognito<br>User Pool]
        APIGW[API Gateway<br>+ Cognito Authorizer]
        Lambda[Lambda Functions]
    end
    
    App -->|1. サインイン| Cognito
    Cognito -->|2. JWT トークン| App
    App -->|3. API リクエスト<br>+ Bearer Token| APIGW
    APIGW -->|4. トークン検証| Cognito
    APIGW -->|5. 認証済みリクエスト| Lambda
```

### Cognito ヘルパー（cognito_helper.py）

```python
"""Amazon Cognito ヘルパー"""
import os
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

from shared.exceptions import AuthenticationError, ValidationError


logger = Logger()


class CognitoHelper:
    """Cognito操作ヘルパークラス"""
    
    def __init__(self):
        self.client = boto3.client("cognito-idp")
        self.user_pool_id = os.environ.get("COGNITO_USER_POOL_ID")
        self.client_id = os.environ.get("COGNITO_CLIENT_ID")
    
    def sign_up(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """ユーザー登録"""
        
        try:
            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "name", "Value": name},
                ],
            )
            
            return {
                "user_id": response["UserSub"],
                "email": email,
                "confirmed": response["UserConfirmed"],
            }
        except self.client.exceptions.UsernameExistsException:
            raise ValidationError("このメールアドレスは既に登録されています")
        except self.client.exceptions.InvalidPasswordException as e:
            raise ValidationError(f"パスワードが要件を満たしていません: {e}")
        except ClientError as e:
            logger.error(f"Sign up failed: {e}")
            raise AuthenticationError("ユーザー登録に失敗しました")
    
    def confirm_sign_up(self, email: str, confirmation_code: str) -> bool:
        """メール確認"""
        
        try:
            self.client.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code,
            )
            return True
        except self.client.exceptions.CodeMismatchException:
            raise ValidationError("確認コードが正しくありません")
        except self.client.exceptions.ExpiredCodeException:
            raise ValidationError("確認コードの有効期限が切れています")
        except ClientError as e:
            logger.error(f"Confirm sign up failed: {e}")
            raise AuthenticationError("メール確認に失敗しました")
    
    def sign_in(self, email: str, password: str) -> Dict[str, str]:
        """サインイン"""
        
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password,
                },
            )
            
            auth_result = response["AuthenticationResult"]
            return {
                "access_token": auth_result["AccessToken"],
                "id_token": auth_result["IdToken"],
                "refresh_token": auth_result["RefreshToken"],
                "expires_in": auth_result["ExpiresIn"],
                "token_type": "Bearer",
            }
        except self.client.exceptions.NotAuthorizedException:
            raise AuthenticationError("メールアドレスまたはパスワードが正しくありません")
        except self.client.exceptions.UserNotConfirmedException:
            raise AuthenticationError("メールアドレスが確認されていません")
        except ClientError as e:
            logger.error(f"Sign in failed: {e}")
            raise AuthenticationError("サインインに失敗しました")
    
    def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        """トークンリフレッシュ"""
        
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={
                    "REFRESH_TOKEN": refresh_token,
                },
            )
            
            auth_result = response["AuthenticationResult"]
            return {
                "access_token": auth_result["AccessToken"],
                "id_token": auth_result["IdToken"],
                "expires_in": auth_result["ExpiresIn"],
                "token_type": "Bearer",
            }
        except self.client.exceptions.NotAuthorizedException:
            raise AuthenticationError("リフレッシュトークンが無効です")
        except ClientError as e:
            logger.error(f"Token refresh failed: {e}")
            raise AuthenticationError("トークンの更新に失敗しました")
    
    def forgot_password(self, email: str) -> bool:
        """パスワードリセット要求"""
        
        try:
            self.client.forgot_password(
                ClientId=self.client_id,
                Username=email,
            )
            return True
        except self.client.exceptions.UserNotFoundException:
            # セキュリティのため、ユーザーが存在しなくても成功を返す
            return True
        except ClientError as e:
            logger.error(f"Forgot password failed: {e}")
            raise AuthenticationError("パスワードリセットの要求に失敗しました")
    
    def confirm_forgot_password(
        self, email: str, confirmation_code: str, new_password: str
    ) -> bool:
        """パスワードリセット確認"""
        
        try:
            self.client.confirm_forgot_password(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code,
                Password=new_password,
            )
            return True
        except self.client.exceptions.CodeMismatchException:
            raise ValidationError("確認コードが正しくありません")
        except self.client.exceptions.ExpiredCodeException:
            raise ValidationError("確認コードの有効期限が切れています")
        except self.client.exceptions.InvalidPasswordException as e:
            raise ValidationError(f"パスワードが要件を満たしていません: {e}")
        except ClientError as e:
            logger.error(f"Confirm forgot password failed: {e}")
            raise AuthenticationError("パスワードリセットに失敗しました")
    
    def get_user(self, access_token: str) -> Dict[str, Any]:
        """ユーザー情報取得"""
        
        try:
            response = self.client.get_user(AccessToken=access_token)
            
            attributes = {
                attr["Name"]: attr["Value"]
                for attr in response.get("UserAttributes", [])
            }
            
            return {
                "user_id": attributes.get("sub"),
                "email": attributes.get("email"),
                "name": attributes.get("name", ""),
                "email_verified": attributes.get("email_verified") == "true",
            }
        except self.client.exceptions.NotAuthorizedException:
            raise AuthenticationError("トークンが無効です")
        except ClientError as e:
            logger.error(f"Get user failed: {e}")
            raise AuthenticationError("ユーザー情報の取得に失敗しました")
    
    def sign_out(self, access_token: str) -> bool:
        """サインアウト（グローバル）"""
        
        try:
            self.client.global_sign_out(AccessToken=access_token)
            return True
        except ClientError as e:
            logger.error(f"Sign out failed: {e}")
            return False
```

### 認証ハンドラー（auth_handler.py）

```python
"""認証ハンドラー"""
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, EmailStr, Field

from auth.cognito_helper import CognitoHelper
from shared.responses import success_response, error_response


logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()
cognito = CognitoHelper()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=100)


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class ConfirmSignUpRequest(BaseModel):
    email: EmailStr
    confirmation_code: str = Field(min_length=6, max_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@app.post("/auth/signup")
@tracer.capture_method
def sign_up():
    """ユーザー登録"""
    body = app.current_event.json_body
    request = SignUpRequest(**body)
    
    result = cognito.sign_up(
        email=request.email,
        password=request.password,
        name=request.name,
    )
    
    return success_response(
        data=result,
        message="確認メールを送信しました",
        status_code=201,
    )


@app.post("/auth/signup/confirm")
@tracer.capture_method
def confirm_sign_up():
    """メール確認"""
    body = app.current_event.json_body
    request = ConfirmSignUpRequest(**body)
    
    cognito.confirm_sign_up(
        email=request.email,
        confirmation_code=request.confirmation_code,
    )
    
    return success_response(message="メールアドレスが確認されました")


@app.post("/auth/signin")
@tracer.capture_method
def sign_in():
    """サインイン"""
    body = app.current_event.json_body
    request = SignInRequest(**body)
    
    tokens = cognito.sign_in(
        email=request.email,
        password=request.password,
    )
    
    return success_response(data=tokens)


@app.post("/auth/refresh")
@tracer.capture_method
def refresh():
    """トークンリフレッシュ"""
    body = app.current_event.json_body
    request = RefreshTokenRequest(**body)
    
    tokens = cognito.refresh_tokens(refresh_token=request.refresh_token)
    
    return success_response(data=tokens)


@app.post("/auth/signout")
@tracer.capture_method
def sign_out():
    """サインアウト"""
    auth_header = app.current_event.get_header_value("Authorization") or ""
    token = auth_header.replace("Bearer ", "")
    
    cognito.sign_out(access_token=token)
    
    return success_response(message="サインアウトしました")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
```

### リクエストからユーザー情報取得（user_context.py）

```python
"""ユーザーコンテキスト"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class UserContext:
    """認証済みユーザー情報"""
    
    user_id: str
    email: str
    name: str = ""
    email_verified: bool = False
    
    @classmethod
    def from_event(cls, event: dict) -> Optional["UserContext"]:
        """API Gatewayイベントからユーザー情報を取得
        
        Cognito Authorizer使用時、claimsに情報が含まれる
        """
        claims = (
            event.get("requestContext", {})
            .get("authorizer", {})
            .get("claims", {})
        )
        
        if not claims:
            return None
        
        return cls(
            user_id=claims.get("sub", ""),
            email=claims.get("email", ""),
            name=claims.get("name", ""),
            email_verified=claims.get("email_verified") == "true",
        )


def get_user_id_from_event(event: dict) -> str:
    """イベントからユーザーIDを取得"""
    
    user = UserContext.from_event(event)
    if not user:
        raise ValueError("認証情報が見つかりません")
    return user.user_id


def get_user_from_event(event: dict) -> Dict[str, Any]:
    """イベントからユーザー情報を辞書で取得"""
    
    user = UserContext.from_event(event)
    if not user:
        return {}
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "name": user.name,
        "email_verified": user.email_verified,
    }
```

---

## エラーハンドリング

### カスタム例外（exceptions.py）

```python
"""カスタム例外クラス"""
from typing import Optional, List, Dict, Any


class AppException(Exception):
    """アプリケーション例外の基底クラス"""
    
    def __init__(
        self,
        message: str,
        code: str = "ERROR",
        status_code: int = 500,
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


class NotFoundError(AppException):
    """リソースが見つからない"""
    
    def __init__(self, message: str = "リソースが見つかりません"):
        super().__init__(message, "NOT_FOUND", 404)


class ValidationError(AppException):
    """バリデーションエラー"""
    
    def __init__(
        self,
        message: str = "入力データが不正です",
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(message, "VALIDATION_ERROR", 400, details)


class AuthenticationError(AppException):
    """認証エラー"""
    
    def __init__(self, message: str = "認証に失敗しました"):
        super().__init__(message, "UNAUTHORIZED", 401)


class ForbiddenError(AppException):
    """アクセス拒否"""
    
    def __init__(self, message: str = "アクセス権限がありません"):
        super().__init__(message, "FORBIDDEN", 403)


class ConflictError(AppException):
    """競合エラー"""
    
    def __init__(self, message: str = "リソースが既に存在します"):
        super().__init__(message, "CONFLICT", 409)


class DatabaseError(AppException):
    """データベースエラー"""
    
    def __init__(self, message: str = "データベースエラーが発生しました"):
        super().__init__(message, "DATABASE_ERROR", 500)
```

---

## ユーティリティ

### レスポンスヘルパー（responses.py）

```python
"""レスポンスヘルパー"""
import json
from typing import Any, Optional, List, Dict
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    """Decimal対応JSONエンコーダー"""
    
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = 200,
    pagination: Optional[Dict] = None,
) -> dict:
    """成功レスポンスを生成"""
    
    body = {"success": True}
    
    if data is not None:
        # Pydanticモデルの場合は変換
        if hasattr(data, "model_dump"):
            body["data"] = data.model_dump()
        elif isinstance(data, list):
            body["data"] = [
                item.model_dump() if hasattr(item, "model_dump") else item
                for item in data
            ]
        else:
            body["data"] = data
    
    if message:
        body["message"] = message
    
    if pagination:
        body["pagination"] = pagination
    
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, cls=DecimalEncoder, ensure_ascii=False),
    }


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Optional[List[Dict]] = None,
) -> dict:
    """エラーレスポンスを生成"""
    
    body = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    
    if details:
        body["error"]["details"] = details
    
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }
```

### ページネーション（pagination.py）

```python
"""ページネーションヘルパー"""
from typing import List, Any, Optional
import math


def paginate(
    items: List[Any],
    total_count: int,
    page: int,
    per_page: int,
    next_cursor: Optional[str] = None,
) -> dict:
    """ページネーションメタ情報を生成"""
    
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 0
    
    return {
        "page": page,
        "per_page": per_page,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages or next_cursor is not None,
        "has_prev": page > 1,
        "next_cursor": next_cursor,
    }
```

---

## テスト

### Pytestフィクスチャ（conftest.py）

```python
"""Pytestフィクスチャ"""
import os
import pytest
import boto3
from moto import mock_dynamodb

# テスト用環境変数
os.environ["TABLE_NAME"] = "test-table"
os.environ["JWT_SECRET"] = "test-secret-key"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def dynamodb_table():
    """DynamoDBテーブルモック"""
    
    with mock_dynamodb():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        
        table = dynamodb.create_table(
            TableName="test-table",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        
        table.wait_until_exists()
        
        yield table


@pytest.fixture
def api_gateway_event():
    """API Gatewayイベント生成ヘルパー"""
    
    def _event(
        method: str = "GET",
        path: str = "/",
        body: dict = None,
        path_params: dict = None,
        query_params: dict = None,
        user_id: str = "test-user-id",
    ):
        return {
            "httpMethod": method,
            "path": path,
            "body": json.dumps(body) if body else None,
            "pathParameters": path_params,
            "queryStringParameters": query_params,
            "requestContext": {
                "authorizer": {
                    "user_id": user_id,
                    "email": "test@example.com",
                    "role": "user",
                }
            },
            "headers": {
                "Content-Type": "application/json",
            },
        }
    
    return _event


@pytest.fixture
def jwt_token():
    """JWTトークン生成"""
    
    from auth.jwt_handler import JWTHandler
    
    handler = JWTHandler()
    return handler.create_access_token({
        "user_id": "test-user-id",
        "email": "test@example.com",
        "role": "user",
    })
```

### ハンドラーテスト（test_handler.py）

```python
"""ハンドラーテスト"""
import json
import pytest
from handlers.crud_handler import lambda_handler


class TestProjectHandler:
    """プロジェクトハンドラーテスト"""
    
    def test_create_project(self, dynamodb_table, api_gateway_event):
        """プロジェクト作成テスト"""
        
        event = api_gateway_event(
            method="POST",
            path="/projects",
            body={"name": "Test Project", "description": "Test description"},
        )
        
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["data"]["name"] == "Test Project"
    
    def test_list_projects(self, dynamodb_table, api_gateway_event):
        """プロジェクト一覧テスト"""
        
        # 先にプロジェクトを作成
        create_event = api_gateway_event(
            method="POST",
            path="/projects",
            body={"name": "Test Project"},
        )
        lambda_handler(create_event, None)
        
        # 一覧取得
        event = api_gateway_event(
            method="GET",
            path="/projects",
        )
        
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert len(body["data"]) >= 1
    
    def test_get_project_not_found(self, dynamodb_table, api_gateway_event):
        """存在しないプロジェクト取得テスト"""
        
        event = api_gateway_event(
            method="GET",
            path="/projects/non-existent-id",
            path_params={"projectId": "non-existent-id"},
        )
        
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["code"] == "NOT_FOUND"
    
    def test_create_project_validation_error(self, dynamodb_table, api_gateway_event):
        """バリデーションエラーテスト"""
        
        event = api_gateway_event(
            method="POST",
            path="/projects",
            body={"name": ""},  # 空の名前
        )
        
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"
```

---

## 関連ドキュメント

| ドキュメント | パス | 説明 |
|-------------|------|------|
| システム概要 | [../overview.md](../overview.md) | システム全体の概要 |
| ガイドインデックス | [index.md](./index.md) | ガイド一覧 |
| OpenAPI→Lambda変換ガイド | [openapi-to-lambda.md](./openapi-to-lambda.md) | Lambda実装方法 |
| API GW + Lambda デプロイガイド | [aws-lambda-deployment.md](./aws-lambda-deployment.md) | Lambdaデプロイ方法 |

---

## 変更履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.0.0 | 2025-12-30 | 初版作成 |

---

**作成日**: 2025-12-30  
**メンテナー**: auto_deploy プロジェクトチーム
