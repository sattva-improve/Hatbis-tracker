# Habit Tracker RPG API リファレンス

このドキュメントでは、Habit Tracker RPG API の全エンドポイントについて、リクエスト・レスポンス例を含めて詳細に説明します。

## 📋 目次

1. [認証 (Auth)](#認証-auth)
2. [ユーザー (Users)](#ユーザー-users)
3. [習慣 (Habits)](#習慣-habits)
4. [記録 (Records)](#記録-records)
5. [統計 (Stats)](#統計-stats)
6. [アチーブメント (Achievements)](#アチーブメント-achievements)
7. [ジョブ (Jobs)](#ジョブ-jobs)

## 🔑 認証について

すべてのAPI（`/auth/*` を除く）は認証が必要です。リクエストヘッダーに以下を含めてください：

```
Authorization: Bearer {access_token}
```

---

## 認証 (Auth)

### POST /auth/signup - ユーザー登録

新規ユーザーを登録します。

**リクエスト:**
```json
{
  "email": "test@example.com",
  "password": "SecurePass123!",
  "display_name": "テストユーザー",
  "timezone": "Asia/Tokyo"
}
```

**レスポンス (201 Created):**
```json
{
  "message": "ユーザー登録が完了しました",
  "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
  "user": {
    "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
    "email": "test@example.com",
    "profile": {
      "display_name": "テストユーザー",
      "avatar_url": null,
      "bio": null,
      "timezone": "Asia/Tokyo"
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
      "strength_exp": 0
    },
    "level": 1,
    "total_exp": 0,
    "current_job_id": "beginner",
    "max_streak": 0,
    "current_streak": 0,
    "created_at": "2026-01-08T10:00:00.000000",
    "updated_at": "2026-01-08T10:00:00.000000",
    "last_login_at": null
  }
}
```

**エラーレスポンス (400 Bad Request):**
```json
{
  "code": "MISSING_FIELDS",
  "message": "email, password, display_name は必須です"
}
```

**エラーレスポンス (409 Conflict):**
```json
{
  "code": "USER_EXISTS",
  "message": "このメールアドレスは既に登録されています"
}
```

### POST /auth/signin - ログイン

ユーザーの認証を行い、アクセストークンを取得します。

**リクエスト:**
```json
{
  "email": "test@example.com",
  "password": "SecurePass123!"
}
```

**レスポンス (200 OK):**
```json
{
  "access_token": "eyJraWQiOiJhYmNkZWYxMjM0NTY3ODkwIiwiYWxnIjoiUlMyNTYifQ...",
  "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

**エラーレスポンス (401 Unauthorized):**
```json
{
  "code": "INVALID_CREDENTIALS",
  "message": "メールアドレスまたはパスワードが間違っています"
}
```

### POST /auth/refresh - トークンリフレッシュ

リフレッシュトークンを使用して新しいアクセストークンを取得します。

**リクエスト:**
```json
{
  "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ..."
}
```

**レスポンス (200 OK):**
```json
{
  "access_token": "eyJraWQiOiJhYmNkZWYxMjM0NTY3ODkwIiwiYWxnIjoiUlMyNTYifQ...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### POST /auth/signout - ログアウト

現在のセッションを終了します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**レスポンス (204 No Content):**
レスポンスボディなし

### POST /auth/change-password - パスワード変更

ログイン中のユーザーのパスワードを変更します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**リクエスト:**
```json
{
  "old_password": "OldSecurePass123!",
  "new_password": "NewSecurePass456!"
}
```

**レスポンス (200 OK):**
```json
{
  "message": "パスワードを変更しました"
}
```

---

## SSO (ソーシャルログイン) 🆕

### GET /auth/sso/providers - SSOプロバイダー一覧

利用可能なSSOプロバイダーとログインURLを取得します。

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| redirect_uri | string | No | コールバックURL（デフォルト: http://localhost:3000/auth/callback） |

**レスポンス (200 OK):**
```json
{
  "providers": {
    "google": {
      "name": "Google",
      "icon": "🔵",
      "login_url": "https://habit-tracker-rpg-dev-auth.auth.ap-northeast-1.amazoncognito.com/oauth2/authorize?identity_provider=Google&client_id=xxx&redirect_uri=http://localhost:3000/auth/callback&response_type=code&scope=email+openid+profile"
    },
    "apple": {
      "name": "Apple",
      "icon": "🍎",
      "login_url": "https://habit-tracker-rpg-dev-auth.auth.ap-northeast-1.amazoncognito.com/oauth2/authorize?identity_provider=SignInWithApple&client_id=xxx&redirect_uri=http://localhost:3000/auth/callback&response_type=code&scope=email+openid+profile"
    }
  },
  "cognito_hosted_ui": "https://habit-tracker-rpg-dev-auth.auth.ap-northeast-1.amazoncognito.com/login?client_id=xxx&redirect_uri=http://localhost:3000/auth/callback&response_type=code&scope=email+openid+profile"
}
```

### GET /auth/sso/callback - SSOコールバック

OAuth認可コードをトークンに交換します。通常はCognito Hosted UIからリダイレクトで呼び出されます。

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| code | string | Yes | 認可コード |
| redirect_uri | string | No | 元のリダイレクトURI |

**レスポンス (200 OK):**
```json
{
  "access_token": "eyJraWQiOi...",
  "id_token": "eyJraWQiOi...",
  "refresh_token": "eyJjdHkiOi...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "user": {
    "user_id": "google_123456789012345678901",
    "email": "user@gmail.com",
    "display_name": "User Name",
    "auth_provider": "Google"
  }
}
```

**エラーレスポンス (400 Bad Request):**
```json
{
  "error": {
    "code": "SSO_ERROR",
    "message": "認証がキャンセルされました"
  }
}
```

### GET /auth/me - 現在のユーザー情報

アクセストークンから現在のユーザー情報を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**レスポンス (200 OK):**
```json
{
  "user_id": "google_123456789012345678901",
  "email": "user@gmail.com",
  "display_name": "User Name",
  "timezone": "Asia/Tokyo",
  "email_verified": true,
  "user_data": {
    "user_id": "google_123456789012345678901",
    "level": 5,
    "total_exp": 450,
    "stats": {
      "vitality": 3,
      "intelligence": 2,
      "mental": 4,
      "dexterity": 1,
      "charisma": 2,
      "strength": 3
    }
  }
}
```

---

## ユーザー (Users)

### GET /users/me - 自分のプロフィール取得

ログイン中のユーザーの詳細情報を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**レスポンス (200 OK):**
```json
{
  "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
  "email": "test@example.com",
  "profile": {
    "display_name": "テストユーザー",
    "avatar_url": "https://example.com/avatar.png",
    "bio": "習慣化を頑張っています！",
    "timezone": "Asia/Tokyo"
  },
  "stats": {
    "vitality": 5,
    "intelligence": 3,
    "mental": 4,
    "dexterity": 2,
    "charisma": 2,
    "strength": 6,
    "vitality_exp": 450,
    "intelligence_exp": 200,
    "mental_exp": 350,
    "dexterity_exp": 100,
    "charisma_exp": 100,
    "strength_exp": 550
  },
  "level": 8,
  "total_exp": 1750,
  "current_job_id": "warrior_apprentice",
  "max_streak": 14,
  "current_streak": 7,
  "created_at": "2026-01-01T00:00:00.000000",
  "updated_at": "2026-01-08T10:00:00.000000",
  "last_login_at": "2026-01-08T09:00:00.000000"
}
```

### PUT /users/me - プロフィール更新

ログイン中のユーザーのプロフィールを更新します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**リクエスト:**
```json
{
  "display_name": "新しい名前",
  "avatar_url": "https://example.com/new-avatar.png",
  "bio": "更新した自己紹介文です"
}
```

**レスポンス (200 OK):**
```json
{
  "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
  "email": "test@example.com",
  "profile": {
    "display_name": "新しい名前",
    "avatar_url": "https://example.com/new-avatar.png",
    "bio": "更新した自己紹介文です",
    "timezone": "Asia/Tokyo"
  },
  "stats": {
    "vitality": 5,
    "intelligence": 3,
    "mental": 4,
    "dexterity": 2,
    "charisma": 2,
    "strength": 6,
    "vitality_exp": 450,
    "intelligence_exp": 200,
    "mental_exp": 350,
    "dexterity_exp": 100,
    "charisma_exp": 100,
    "strength_exp": 550
  },
  "level": 8,
  "total_exp": 1750,
  "current_job_id": "warrior_apprentice",
  "max_streak": 14,
  "current_streak": 7,
  "created_at": "2026-01-01T00:00:00.000000",
  "updated_at": "2026-01-08T10:05:00.000000",
  "last_login_at": "2026-01-08T09:00:00.000000"
}
```

### GET /users/me/stats - 自分のステータス詳細取得

ログイン中のユーザーの各ステータスの詳細（現在の経験値、次のレベルまでの経験値など）を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**レスポンス (200 OK):**
```json
{
  "vitality": 5,
  "vitality_exp": 450,
  "vitality_next_level_exp": 113,
  "intelligence": 3,
  "intelligence_exp": 200,
  "intelligence_next_level_exp": 50,
  "mental": 4,
  "mental_exp": 350,
  "mental_next_level_exp": 88,
  "dexterity": 2,
  "dexterity_exp": 100,
  "dexterity_next_level_exp": 50,
  "charisma": 2,
  "charisma_exp": 100,
  "charisma_next_level_exp": 50,
  "strength": 6,
  "strength_exp": 550,
  "strength_next_level_exp": 269
}
```

---

## 習慣 (Habits)

### GET /habits - 習慣一覧取得

ユーザーの習慣一覧を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| category | string | No | 習慣カテゴリでフィルタ |
| is_active | boolean | No | アクティブ状態でフィルタ (default: true) |
| is_archived | boolean | No | アーカイブ状態でフィルタ (default: false) |

**レスポンス (200 OK):**
```json
{
  "habits": [
    {
      "habit_id": "01HRQY5K4MZJP7Y9GF2D5N3B6C",
      "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
      "name": "朝のジョギング",
      "description": "毎朝30分のジョギングをする",
      "icon": "🏃",
      "color": "#4CAF50",
      "category": "exercise",
      "stat_type": "VIT",
      "frequency": {
        "type": "daily",
        "times_per_week": null,
        "specific_days": null
      },
      "difficulty": "normal",
      "reminder_enabled": true,
      "reminder_time": "06:30:00",
      "current_streak": 7,
      "best_streak": 14,
      "total_completions": 45,
      "is_active": true,
      "is_archived": false,
      "created_at": "2026-01-01T00:00:00.000000",
      "updated_at": "2026-01-08T06:35:00.000000",
      "last_completed_at": "2026-01-08T06:35:00.000000"
    },
    {
      "habit_id": "01HRQY6K4MZJP7Y9GF2D5N3B6D",
      "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
      "name": "筋トレ",
      "description": "週3回の筋力トレーニング",
      "icon": "💪",
      "color": "#FF5722",
      "category": "workout",
      "stat_type": "STR",
      "frequency": {
        "type": "specific_days",
        "times_per_week": null,
        "specific_days": [0, 2, 4]
      },
      "difficulty": "hard",
      "reminder_enabled": true,
      "reminder_time": "19:00:00",
      "current_streak": 3,
      "best_streak": 8,
      "total_completions": 24,
      "is_active": true,
      "is_archived": false,
      "created_at": "2026-01-01T00:00:00.000000",
      "updated_at": "2026-01-06T19:30:00.000000",
      "last_completed_at": "2026-01-06T19:30:00.000000"
    }
  ],
  "total": 2
}
```

### POST /habits - 習慣作成

新しい習慣を作成します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**リクエスト:**
```json
{
  "name": "読書",
  "description": "毎日30分の読書",
  "icon": "📚",
  "color": "#2196F3",
  "category": "reading",
  "frequency": {
    "type": "daily"
  },
  "difficulty": "normal",
  "reminder_enabled": true,
  "reminder_time": "21:00:00"
}
```

**レスポンス (201 Created):**
```json
{
  "habit_id": "01HRQZ7K4MZJP7Y9GF2D5N3B6E",
  "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
  "name": "読書",
  "description": "毎日30分の読書",
  "icon": "📚",
  "color": "#2196F3",
  "category": "reading",
  "stat_type": "INT",
  "frequency": {
    "type": "daily",
    "times_per_week": null,
    "specific_days": null
  },
  "difficulty": "normal",
  "reminder_enabled": true,
  "reminder_time": "21:00:00",
  "current_streak": 0,
  "best_streak": 0,
  "total_completions": 0,
  "is_active": true,
  "is_archived": false,
  "created_at": "2026-01-08T10:00:00.000000",
  "updated_at": "2026-01-08T10:00:00.000000",
  "last_completed_at": null
}
```

**カテゴリ一覧:**

| カテゴリ | 説明 | 対応ステータス |
|---------|------|---------------|
| exercise | 運動 | VIT |
| sleep | 睡眠 | VIT |
| health | 健康 | VIT |
| reading | 読書 | INT |
| study | 勉強 | INT |
| learning | 学習 | INT |
| meditation | 瞑想 | MND |
| journaling | 日記 | MND |
| gratitude | 感謝 | MND |
| mindfulness | マインドフルネス | MND |
| music | 音楽 | DEX |
| art | アート | DEX |
| craft | クラフト | DEX |
| hobby | 趣味 | DEX |
| communication | コミュニケーション | CHA |
| social | 社交 | CHA |
| grooming | 身だしなみ | CHA |
| workout | 筋トレ | STR |
| sports | スポーツ | STR |
| fitness | フィットネス | STR |
| other | その他 | VIT |

### GET /habits/{habitId} - 習慣詳細取得

指定した習慣の詳細を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**レスポンス (200 OK):**
```json
{
  "habit_id": "01HRQY5K4MZJP7Y9GF2D5N3B6C",
  "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
  "name": "朝のジョギング",
  "description": "毎朝30分のジョギングをする",
  "icon": "🏃",
  "color": "#4CAF50",
  "category": "exercise",
  "stat_type": "VIT",
  "frequency": {
    "type": "daily",
    "times_per_week": null,
    "specific_days": null
  },
  "difficulty": "normal",
  "reminder_enabled": true,
  "reminder_time": "06:30:00",
  "current_streak": 7,
  "best_streak": 14,
  "total_completions": 45,
  "is_active": true,
  "is_archived": false,
  "created_at": "2026-01-01T00:00:00.000000",
  "updated_at": "2026-01-08T06:35:00.000000",
  "last_completed_at": "2026-01-08T06:35:00.000000"
}
```

**エラーレスポンス (404 Not Found):**
```json
{
  "code": "HABIT_NOT_FOUND",
  "message": "習慣が見つかりません"
}
```

### PUT /habits/{habitId} - 習慣更新

指定した習慣を更新します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**リクエスト:**
```json
{
  "name": "朝のジョギング（更新）",
  "description": "毎朝45分のジョギングをする",
  "difficulty": "hard"
}
```

**レスポンス (200 OK):**
```json
{
  "habit_id": "01HRQY5K4MZJP7Y9GF2D5N3B6C",
  "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
  "name": "朝のジョギング（更新）",
  "description": "毎朝45分のジョギングをする",
  "icon": "🏃",
  "color": "#4CAF50",
  "category": "exercise",
  "stat_type": "VIT",
  "frequency": {
    "type": "daily",
    "times_per_week": null,
    "specific_days": null
  },
  "difficulty": "hard",
  "reminder_enabled": true,
  "reminder_time": "06:30:00",
  "current_streak": 7,
  "best_streak": 14,
  "total_completions": 45,
  "is_active": true,
  "is_archived": false,
  "created_at": "2026-01-01T00:00:00.000000",
  "updated_at": "2026-01-08T10:10:00.000000",
  "last_completed_at": "2026-01-08T06:35:00.000000"
}
```

### DELETE /habits/{habitId} - 習慣削除

指定した習慣を削除します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**レスポンス (204 No Content):**
レスポンスボディなし

### POST /habits/{habitId}/archive - 習慣アーカイブ

指定した習慣をアーカイブします。アーカイブされた習慣は一覧には表示されませんが、データは保持されます。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**レスポンス (200 OK):**
```json
{
  "habit_id": "01HRQY5K4MZJP7Y9GF2D5N3B6C",
  "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
  "name": "朝のジョギング",
  "description": "毎朝30分のジョギングをする",
  "icon": "🏃",
  "color": "#4CAF50",
  "category": "exercise",
  "stat_type": "VIT",
  "frequency": {
    "type": "daily",
    "times_per_week": null,
    "specific_days": null
  },
  "difficulty": "normal",
  "reminder_enabled": true,
  "reminder_time": "06:30:00",
  "current_streak": 7,
  "best_streak": 14,
  "total_completions": 45,
  "is_active": false,
  "is_archived": true,
  "created_at": "2026-01-01T00:00:00.000000",
  "updated_at": "2026-01-08T10:15:00.000000",
  "last_completed_at": "2026-01-08T06:35:00.000000"
}
```

---

## 記録 (Records)

### GET /habits/{habitId}/records - 習慣記録一覧取得

指定した習慣の記録一覧を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| start_date | string (date) | No | 検索開始日 (YYYY-MM-DD) |
| end_date | string (date) | No | 検索終了日 (YYYY-MM-DD) |

**レスポンス (200 OK):**
```json
{
  "records": [
    {
      "record_id": "01HRR15K4MZJP7Y9GF2D5N3B6F",
      "habit_id": "01HRQY5K4MZJP7Y9GF2D5N3B6C",
      "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
      "completed_date": "2026-01-08",
      "completed": true,
      "note": "今日も頑張った！",
      "exp_earned": 12,
      "streak_at_completion": 7,
      "created_at": "2026-01-08T06:35:00.000000"
    },
    {
      "record_id": "01HRR14K4MZJP7Y9GF2D5N3B6G",
      "habit_id": "01HRQY5K4MZJP7Y9GF2D5N3B6C",
      "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
      "completed_date": "2026-01-07",
      "completed": true,
      "note": null,
      "exp_earned": 12,
      "streak_at_completion": 6,
      "created_at": "2026-01-07T06:40:00.000000"
    }
  ],
  "total": 2
}
```

### POST /habits/{habitId}/records - 習慣記録作成（達成報告）

習慣の達成を記録します。記録すると経験値が加算され、ストリークが更新されます。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**リクエスト:**
```json
{
  "completed_date": "2026-01-08",
  "completed": true,
  "note": "朝から気持ちよく走れた！"
}
```

**レスポンス (201 Created):**
```json
{
  "record": {
    "record_id": "01HRR15K4MZJP7Y9GF2D5N3B6F",
    "habit_id": "01HRQY5K4MZJP7Y9GF2D5N3B6C",
    "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
    "completed_date": "2026-01-08",
    "completed": true,
    "note": "朝から気持ちよく走れた！",
    "exp_earned": 12,
    "streak_at_completion": 8,
    "created_at": "2026-01-08T06:35:00.000000"
  },
  "exp_gained": 12,
  "new_streak": 8,
  "level_up": false,
  "new_level": null,
  "stat_level_up": false,
  "new_stat_level": null,
  "stat_type": "VIT",
  "new_achievements": [],
  "new_jobs": []
}
```

**レスポンス (201 Created) - アチーブメント解除時:**
```json
{
  "record": {
    "record_id": "01HRR15K4MZJP7Y9GF2D5N3B6F",
    "habit_id": "01HRQY5K4MZJP7Y9GF2D5N3B6C",
    "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
    "completed_date": "2026-01-08",
    "completed": true,
    "note": "7日連続達成！",
    "exp_earned": 12,
    "streak_at_completion": 7,
    "created_at": "2026-01-08T06:35:00.000000"
  },
  "exp_gained": 12,
  "new_streak": 7,
  "level_up": true,
  "new_level": 9,
  "stat_level_up": true,
  "new_stat_level": 6,
  "stat_type": "VIT",
  "new_achievements": [
    {
      "achievement_id": "streak_7",
      "name": "一週間の習慣",
      "description": "7日連続で習慣を達成する",
      "icon": "🔥",
      "type": "streak",
      "rarity": "uncommon",
      "exp_reward": 100
    }
  ],
  "new_jobs": []
}
```

### GET /records/today - 今日の達成状況取得

今日予定されている全習慣と、その達成状況を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**レスポンス (200 OK):**
```json
{
  "date": "2026-01-08",
  "habits": [
    {
      "habit": {
        "habit_id": "01HRQY5K4MZJP7Y9GF2D5N3B6C",
        "name": "朝のジョギング",
        "icon": "🏃",
        "category": "exercise"
      },
      "record": {
        "record_id": "01HRR15K4MZJP7Y9GF2D5N3B6F",
        "completed": true,
        "exp_earned": 12
      },
      "is_due_today": true
    },
    {
      "habit": {
        "habit_id": "01HRQZ7K4MZJP7Y9GF2D5N3B6E",
        "name": "読書",
        "icon": "📚",
        "category": "reading"
      },
      "record": null,
      "is_due_today": true
    }
  ],
  "completed_count": 1,
  "total_due": 2,
  "completion_rate": 0.5
}
```

---

## 統計 (Stats)

### GET /stats/daily - 日次統計取得

指定した日の統計情報を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| date | string (date) | Yes | 対象日 (YYYY-MM-DD) |

**レスポンス (200 OK):**
```json
{
  "date": "2026-01-08",
  "total_habits": 3,
  "completed_habits": 2,
  "completion_rate": 0.67,
  "total_exp_earned": 27
}
```

### GET /stats/weekly - 週次統計取得

指定した週の統計情報を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| week_start | string (date) | Yes | 週の開始日 (YYYY-MM-DD、月曜日) |

**レスポンス (200 OK):**
```json
{
  "week_start": "2026-01-06",
  "week_end": "2026-01-12",
  "total_habits": 21,
  "completed_habits": 18,
  "completion_rate": 0.86,
  "total_exp_earned": 198,
  "daily_stats": [
    {
      "date": "2026-01-06",
      "total_habits": 3,
      "completed_habits": 3,
      "completion_rate": 1.0,
      "total_exp_earned": 30
    },
    {
      "date": "2026-01-07",
      "total_habits": 3,
      "completed_habits": 3,
      "completion_rate": 1.0,
      "total_exp_earned": 30
    },
    {
      "date": "2026-01-08",
      "total_habits": 3,
      "completed_habits": 2,
      "completion_rate": 0.67,
      "total_exp_earned": 27
    }
  ]
}
```

### GET /stats/monthly - 月次統計取得

指定した月の統計情報を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| year | integer | Yes | 年 (YYYY) |
| month | integer | Yes | 月 (1-12) |

**レスポンス (200 OK):**
```json
{
  "year": 2026,
  "month": 1,
  "total_habits": 93,
  "completed_habits": 82,
  "completion_rate": 0.88,
  "total_exp_earned": 984
}
```

---

## アチーブメント (Achievements)

### GET /achievements - アチーブメント一覧取得

ユーザーのアチーブメント一覧（解除済み・未解除含む）を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| include_locked | boolean | No | 未解除のアチーブメントを含めるか (default: true) |

**レスポンス (200 OK):**
```json
{
  "achievements": [
    {
      "achievement_id": "first_habit",
      "achievement": {
        "achievement_id": "first_habit",
        "name": "最初の習慣",
        "description": "最初の習慣を作成する",
        "icon": "🎉",
        "type": "first",
        "rarity": "common",
        "condition": {"type": "first_habit"},
        "exp_reward": 20,
        "is_hidden": false,
        "sort_order": 0
      },
      "is_unlocked": true,
      "unlocked_at": "2026-01-01T00:00:00.000000",
      "current_value": 1,
      "target_value": 1,
      "progress_percent": 100.0
    },
    {
      "achievement_id": "streak_7",
      "achievement": {
        "achievement_id": "streak_7",
        "name": "一週間の習慣",
        "description": "7日連続で習慣を達成する",
        "icon": "🔥",
        "type": "streak",
        "rarity": "uncommon",
        "condition": {"type": "streak", "days": 7},
        "exp_reward": 100,
        "is_hidden": false,
        "sort_order": 1
      },
      "is_unlocked": true,
      "unlocked_at": "2026-01-08T06:35:00.000000",
      "current_value": 7,
      "target_value": 7,
      "progress_percent": 100.0
    },
    {
      "achievement_id": "streak_30",
      "achievement": {
        "achievement_id": "streak_30",
        "name": "月間マスター",
        "description": "30日連続で習慣を達成する",
        "icon": "🔥",
        "type": "streak",
        "rarity": "rare",
        "condition": {"type": "streak", "days": 30},
        "exp_reward": 500,
        "is_hidden": false,
        "sort_order": 2
      },
      "is_unlocked": false,
      "unlocked_at": null,
      "current_value": 7,
      "target_value": 30,
      "progress_percent": 23.3
    }
  ],
  "unlocked_count": 2,
  "total_count": 3
}
```

**アチーブメントタイプ:**

| タイプ | 説明 | 例 |
|--------|------|-----|
| first | 初めて系 | 最初の習慣作成 |
| streak | 連続達成系 | 7日連続、30日連続など |
| total | 累計系 | 累計100回達成など |
| level | レベル系 | レベル10到達など |
| stat | ステータス系 | VITが10に到達など |
| special | 特殊 | 隠しアチーブメントなど |

**レアリティ:**

| レアリティ | 説明 |
|-----------|------|
| common | コモン（一般的） |
| uncommon | アンコモン（やや珍しい） |
| rare | レア（珍しい） |
| epic | エピック（非常に珍しい） |
| legendary | レジェンダリー（伝説級） |

---

## ジョブ (Jobs)

### GET /jobs - ジョブ一覧取得

ユーザーのジョブ一覧（解除済み・未解除含む）を取得します。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| include_locked | boolean | No | 未解除のジョブを含めるか (default: true) |

**レスポンス (200 OK):**
```json
{
  "jobs": [
    {
      "job_id": "beginner",
      "job": {
        "job_id": "beginner",
        "name": "ビギナー",
        "description": "すべての冒険者の始まり",
        "icon": "🌱",
        "tier": "novice",
        "requirements": {},
        "stat_bonuses": {},
        "exp_bonus": 1.0,
        "sort_order": 0
      },
      "is_unlocked": true,
      "is_equipped": false,
      "unlocked_at": "2026-01-01T00:00:00.000000",
      "requirements_met": {},
      "progress_details": {}
    },
    {
      "job_id": "warrior_apprentice",
      "job": {
        "job_id": "warrior_apprentice",
        "name": "見習い戦士",
        "description": "筋力を鍛える者",
        "icon": "⚔️",
        "tier": "apprentice",
        "requirements": {"stats": {"STR": 5}},
        "stat_bonuses": {"STR": 1},
        "exp_bonus": 1.05,
        "sort_order": 10
      },
      "is_unlocked": true,
      "is_equipped": true,
      "unlocked_at": "2026-01-05T10:00:00.000000",
      "requirements_met": {"stat_STR": true},
      "progress_details": {
        "stats": {
          "STR": {"current": 6, "required": 5}
        }
      }
    }
  ],
  "unlocked_count": 2,
  "total_count": 2
}
```

### POST /jobs/{jobId}/equip - ジョブ装備

解除済みのジョブを装備します。装備したジョブによりステータスボーナスや経験値ボーナスが得られます。

**ヘッダー:**
```
Authorization: Bearer {access_token}
```

**レスポンス (200 OK):**
```json
{
  "user_id": "01HRQX8K4MZJP7Y9GF2D5N3B6C",
  "email": "test@example.com",
  "profile": {
    "display_name": "テストユーザー",
    "avatar_url": null,
    "bio": null,
    "timezone": "Asia/Tokyo"
  },
  "stats": {
    "vitality": 5,
    "intelligence": 3,
    "mental": 4,
    "dexterity": 2,
    "charisma": 2,
    "strength": 6,
    "vitality_exp": 450,
    "intelligence_exp": 200,
    "mental_exp": 350,
    "dexterity_exp": 100,
    "charisma_exp": 100,
    "strength_exp": 550
  },
  "level": 8,
  "total_exp": 1750,
  "current_job_id": "warrior_apprentice",
  "max_streak": 14,
  "current_streak": 7,
  "created_at": "2026-01-01T00:00:00.000000",
  "updated_at": "2026-01-08T10:20:00.000000",
  "last_login_at": "2026-01-08T09:00:00.000000"
}
```

**エラーレスポンス (400 Bad Request):**
```json
{
  "code": "CANNOT_EQUIP",
  "message": "Job is not unlocked"
}
```

**ジョブティア:**

| ティア | 説明 |
|--------|------|
| novice | 初心者 |
| apprentice | 見習い |
| journeyman | 熟練者 |
| expert | 達人 |
| master | マスター |
| grandmaster | グランドマスター |

---

## 📊 経験値・レベルシステム

> **🎯 60日カンスト設計**: このゲームは毎日コツコツ習慣を続ければ、約60日でレベル99（最大レベル）に到達できるようバランス調整されています。

### 基本経験値の計算

```
基本EXP = 15
難易度係数:
  - easy: 0.5     (7.5 EXP)
  - normal: 1.0   (15 EXP)
  - hard: 1.5     (22.5 EXP)
  - very_hard: 2.0 (30 EXP)

ストリークボーナス（継続日数に応じて増加）:
  - 3日連続: 1.1倍
  - 7日連続: 1.25倍
  - 14日連続: 1.5倍
  - 30日連続: 2.0倍
  - 60日連続: 2.5倍  ← 2ヶ月継続で最大ボーナス！

獲得EXP = 基本EXP × 難易度係数 × ストリークボーナス × ジョブ経験値ボーナス
```

### レベルアップに必要な経験値

```
必要経験値 = 基本経験値 × (成長率 ^ (レベル - 1))

基本経験値: 15
成長率: 1.025
最大レベル: 99
レベル99到達に必要な総経験値: 約4,427 EXP
```

| レベル | 必要経験値 | 累計経験値 |
|--------|-----------|-----------|
| 1 → 2 | 15 | 15 |
| 5 → 6 | 17 | 78 |
| 10 → 11 | 19 | 168 |
| 25 → 26 | 28 | 519 |
| 50 → 51 | 51 | 1,444 |
| 75 → 76 | 93 | 3,098 |
| 98 → 99 | 158 | 4,427 |

### 60日でカンストするモデルケース

| 日数 | ストリーク倍率 | 1日の獲得EXP（3習慣） | 累計EXP | 到達レベル |
|------|---------------|----------------------|---------|-----------|
| 1-2日目 | 1.0x | 45 | 90 | Lv.6 |
| 3-6日目 | 1.1x | 49.5 | 288 | Lv.14 |
| 7-13日目 | 1.25x | 56.25 | 682 | Lv.28 |
| 14-29日目 | 1.5x | 67.5 | 1,762 | Lv.57 |
| 30-59日目 | 2.0x | 90 | 4,462 | Lv.99 🎉 |

**※ 上記は難易度Normalの習慣を毎日3つ達成した場合の例です**

---

## 🔐 エラーコード一覧

| コード | HTTPステータス | 説明 |
|--------|---------------|------|
| MISSING_FIELDS | 400 | 必須フィールドが不足 |
| INVALID_REQUEST | 400 | リクエスト形式が不正 |
| INVALID_CREDENTIALS | 401 | 認証情報が不正 |
| UNAUTHORIZED | 401 | 認証が必要 |
| TOKEN_EXPIRED | 401 | トークンが期限切れ |
| FORBIDDEN | 403 | アクセス権限がない |
| HABIT_NOT_FOUND | 404 | 習慣が見つからない |
| RECORD_NOT_FOUND | 404 | 記録が見つからない |
| USER_NOT_FOUND | 404 | ユーザーが見つからない |
| USER_EXISTS | 409 | ユーザーが既に存在 |
| ALREADY_RECORDED | 409 | 既に記録済み |
| CANNOT_EQUIP | 400 | ジョブを装備できない |
| INTERNAL_ERROR | 500 | サーバー内部エラー |
