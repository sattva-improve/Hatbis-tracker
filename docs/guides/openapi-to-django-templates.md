# OpenAPI → Django 変換テンプレート集

> **ドキュメントバージョン**: 1.1.0  
> **最終更新日**: 2025-12-30  
> **ステータス**: Active

実際のコード生成に使用できるテンプレート集です。

## 目次

1. [settings.py テンプレート](#1-settingspy-テンプレート)
2. [モデルテンプレート](#2-モデルテンプレート)
3. [シリアライザーテンプレート](#3-シリアライザーテンプレート)
4. [ビューテンプレート](#4-ビューテンプレート)
5. [認証ビューテンプレート](#5-認証ビューテンプレート)
6. [テストテンプレート](#6-テストテンプレート)
7. [conftest.py テンプレート](#7-conftestpy-テンプレート)
8. [pytest.ini テンプレート](#8-pytestini-テンプレート)
9. [関連ドキュメント](#9-関連ドキュメント)

---

## 1. settings.py テンプレート

```python
"""
Django settings for {project_name} project.
"""
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '{secret_key}'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # Local
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'api.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.CustomPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOW_ALL_ORIGINS = True

LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

## 2. モデルテンプレート

### カスタムユーザーモデル

```python
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('メールアドレスは必須です')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField('メールアドレス', max_length=255, unique=True)
    name = models.CharField('ユーザー名', max_length=100)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
```

### 基本モデル

```python
class {ModelName}(models.Model):
    """
    {description}
    """
    # ステータス等のchoices
    STATUS_CHOICES = [
        ('value1', 'ラベル1'),
        ('value2', 'ラベル2'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # string fields
    title = models.CharField('タイトル', max_length=100)
    description = models.TextField('説明', max_length=1000, blank=True, default='')
    # enum field
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='value1')
    # foreign key
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='{related_name}')
    # nullable foreign key
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # datetime
    due_date = models.DateTimeField('期限', null=True, blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        db_table = '{table_name}'
        ordering = ['-created_at']
```

---

## 3. シリアライザーテンプレート

### 作成用シリアライザー

```python
class Create{Model}Serializer(serializers.ModelSerializer):
    # camelCase -> snake_case 変換が必要なフィールド
    assigneeId = serializers.UUIDField(required=False, allow_null=True)
    dueDate = serializers.DateTimeField(source='due_date', required=False, allow_null=True)
    
    class Meta:
        model = {Model}
        fields = ['title', 'description', 'status', 'assigneeId', 'dueDate']
        extra_kwargs = {
            'status': {'default': 'todo'},
        }
    
    def validate_assigneeId(self, value):
        if value and not User.objects.filter(id=value).exists():
            raise serializers.ValidationError('指定されたユーザーが存在しません')
        return value
    
    def create(self, validated_data):
        assignee_id = validated_data.pop('assigneeId', None)
        if assignee_id:
            validated_data['assignee'] = User.objects.get(id=assignee_id)
        return super().create(validated_data)
```

### 更新用シリアライザー

```python
class Update{Model}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {Model}
        fields = ['title', 'description', 'status']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'status': {'required': False},
        }
```

### レスポンス用シリアライザー

```python
class {Model}Serializer(serializers.ModelSerializer):
    # ネストしたオブジェクト
    owner = UserSummarySerializer(read_only=True)
    assignee = UserSummarySerializer(read_only=True)
    
    # camelCase フィールド
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    
    # 計算フィールド
    taskCount = serializers.IntegerField(source='task_count', read_only=True)
    
    class Meta:
        model = {Model}
        fields = ['id', 'title', 'description', 'status', 'owner', 'assignee', 
                  'taskCount', 'createdAt', 'updatedAt']
        read_only_fields = ['id', 'createdAt', 'updatedAt']
```

---

## 4. ビューテンプレート

### ViewSet

```python
class {Model}ViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return Create{Model}Serializer
        elif self.action in ['update', 'partial_update']:
            return Update{Model}Serializer
        elif self.action == 'retrieve':
            return {Model}DetailSerializer
        return {Model}Serializer
    
    def get_queryset(self):
        queryset = {Model}.objects.select_related('owner', 'assignee')
        
        # フィルター
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # ソート
        sort = self.request.query_params.get('sort', 'createdAt')
        order = self.request.query_params.get('order', 'desc')
        sort_mapping = {'createdAt': 'created_at', 'updatedAt': 'updated_at'}
        sort_field = sort_mapping.get(sort, 'created_at')
        if order == 'desc':
            sort_field = f'-{sort_field}'
        
        return queryset.order_by(sort_field)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(owner=request.user)
        
        response_serializer = {Model}Serializer(instance)
        return Response({'data': response_serializer.data}, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'data': serializer.data})
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        response_serializer = {Model}Serializer(instance)
        return Response({'data': response_serializer.data})
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
```

### カスタムアクション

```python
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        instance = self.get_object()
        
        new_status = request.data.get('status')
        valid_statuses = ['todo', 'in_progress', 'done']
        
        if new_status not in valid_statuses:
            return Response(
                {'error': {'code': 'VAL_001', 'message': '無効なステータスです'}},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        instance.status = new_status
        instance.save()
        
        serializer = {Model}Serializer(instance)
        return Response({'data': serializer.data})
```

---

## 5. 認証ビューテンプレート

```python
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'data': UserResponseSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'data': {
                'accessToken': str(refresh.access_token),
                'refreshToken': str(refresh),
                'expiresIn': 3600,
                'tokenType': 'Bearer',
            }
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)
```

---

## 6. テストテンプレート

```python
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='TestPass123',
        name='テストユーザー'
    )

@pytest.fixture
def authenticated_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.mark.django_db
class Test{Model}List:
    def test_list_success(self, authenticated_client, test_{model}):
        url = reverse('{model}-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'data' in response.data


@pytest.mark.django_db
class Test{Model}Create:
    def test_create_success(self, authenticated_client):
        url = reverse('{model}-list')
        data = {
            'title': '新規{model}',
            'description': '説明'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['title'] == '新規{model}'


@pytest.mark.django_db
class Test{Model}Detail:
    def test_get_success(self, authenticated_client, test_{model}):
        url = reverse('{model}-detail', kwargs={'pk': test_{model}.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class Test{Model}Update:
    def test_update_success(self, authenticated_client, test_{model}):
        url = reverse('{model}-detail', kwargs={'pk': test_{model}.id})
        data = {'title': '更新後'}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class Test{Model}Delete:
    def test_delete_success(self, authenticated_client, test_{model}):
        url = reverse('{model}-detail', kwargs={'pk': test_{model}.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
```

---

## 7. conftest.py テンプレート

```python
"""
Django settings for pytest
"""

def pytest_configure():
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': False,
    }
```

---

## 8. pytest.ini テンプレート

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_test.py
addopts = -v --tb=short
```

---

## 9. 関連ドキュメント

| ドキュメント | パス | 説明 |
|-------------|------|------|
| システム概要 | [../overview.md](../overview.md) | システム全体の概要 |
| ガイドインデックス | [index.md](./index.md) | ガイド一覧 |
| OpenAPI→Django変換ガイド | [openapi-to-django.md](./openapi-to-django.md) | 変換ルールの解説 |
| AWS ECSデプロイガイド | [aws-ecs-deployment.md](./aws-ecs-deployment.md) | デプロイ手順 |

---

## 変更履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.1.0 | 2025-12-30 | 目次追加、関連ドキュメントセクション追加 |
| 1.0.0 | 2024-12-29 | 初版作成 |

---

**作成日**: 2024-12-29  
**最終更新日**: 2025-12-30  
**メンテナー**: auto_deploy プロジェクトチーム
