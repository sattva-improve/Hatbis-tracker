# SSO (ソーシャルログイン) 設定ガイド

このドキュメントでは、Habit Tracker RPGでGoogle・Appleアカウントを使ったソーシャルログイン（SSO）を設定する方法を説明します。

## 📋 目次

1. [概要](#概要)
2. [対応プロバイダー](#対応プロバイダー)
3. [Google OAuth設定](#google-oauth設定)
4. [Apple Sign-In設定](#apple-sign-in設定)
5. [CDK設定の更新](#cdk設定の更新)
6. [API エンドポイント](#api-エンドポイント)
7. [フロントエンド実装例](#フロントエンド実装例)

---

## 概要

Habit Tracker RPGは、Amazon Cognitoを使用してソーシャルログイン（SSO）をサポートしています。

### 認証フロー

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  Cognito    │────▶│   Google/   │────▶│  Callback   │
│   (App)     │     │  Hosted UI  │     │   Apple     │     │  Handler    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                           ┌───────────────────────────────────────┘
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   Token     │────▶│   Client    │
                    │  Exchange   │     │   (App)     │
                    └─────────────┘     └─────────────┘
```

1. ユーザーがSSO loginボタンをクリック
2. Cognito Hosted UIにリダイレクト
3. 選択したプロバイダー（Google/Apple）で認証
4. 認可コードと共にコールバックURLにリダイレクト
5. 認可コードをトークンに交換
6. アクセストークンでAPIを利用

---

## 対応プロバイダー

| プロバイダー | ステータス | 説明 |
|------------|----------|------|
| 🔵 Google | ✅ 対応 | Googleアカウントでログイン |
| 🍎 Apple | ✅ 対応 | Apple IDでログイン |
| 📧 Email | ✅ 対応 | メール+パスワードでログイン |

---

## Google OAuth設定

### 1. Google Cloud Consoleでプロジェクトを作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成または既存のプロジェクトを選択

### 2. OAuth同意画面を設定

1. 「APIとサービス」→「OAuth同意画面」を選択
2. ユーザータイプ: 外部
3. 必要な情報を入力:
   - アプリ名: Habit Tracker RPG
   - ユーザーサポートメール: your-email@example.com
   - デベロッパー連絡先情報: your-email@example.com

### 3. OAuth 2.0 クライアントIDを作成

1. 「認証情報」→「認証情報を作成」→「OAuth クライアント ID」
2. アプリケーションの種類: ウェブアプリケーション
3. 名前: Habit Tracker RPG
4. 承認済みのリダイレクトURI:
   ```
   https://habit-tracker-rpg-dev-auth.auth.ap-northeast-1.amazoncognito.com/oauth2/idpresponse
   ```
5. 「作成」をクリック
6. **クライアントID**と**クライアントシークレット**をメモ

### 4. スコープを追加

「APIとサービス」→「OAuth同意画面」→「スコープを追加」:
- `email`
- `profile`
- `openid`

---

## Apple Sign-In設定

### 1. Apple Developer Programに登録

[Apple Developer Program](https://developer.apple.com/programs/)に登録（年間$99）

### 2. App IDを作成

1. [Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources/identifiers/list)にアクセス
2. 「Identifiers」→「+」をクリック
3. 「App IDs」を選択
4. 説明とBundle IDを入力
5. 「Sign In with Apple」を有効化

### 3. Services IDを作成

1. 「Identifiers」→「+」→「Services IDs」を選択
2. 説明とIdentifierを入力（例: `com.example.habittracker.auth`）
3. 「Sign In with Apple」を設定:
   - Primary App ID: 上で作成したApp ID
   - Domains: `habit-tracker-rpg-dev-auth.auth.ap-northeast-1.amazoncognito.com`
   - Return URLs: `https://habit-tracker-rpg-dev-auth.auth.ap-northeast-1.amazoncognito.com/oauth2/idpresponse`

### 4. 秘密鍵を作成

1. 「Keys」→「+」をクリック
2. 名前を入力し「Sign In with Apple」を有効化
3. 「Configure」でPrimary App IDを選択
4. 「Continue」→「Register」
5. **Key ID**をメモし、秘密鍵ファイル（.p8）をダウンロード

---

## CDK設定の更新

### 1. 環境変数または設定ファイルを作成

`cdk/config/sso.json`:

```json
{
  "google": {
    "client_id": "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_GOOGLE_CLIENT_SECRET"
  },
  "apple": {
    "client_id": "com.example.habittracker.auth",
    "team_id": "YOUR_TEAM_ID",
    "key_id": "YOUR_KEY_ID",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
  }
}
```

### 2. CDKスタックの設定を更新

`cdk/stacks/main_stack.py`のプレースホルダーを実際の値に置き換え:

```python
# Google Identity Provider
google_provider = cognito.UserPoolIdentityProviderGoogle(
    self,
    "GoogleProvider",
    user_pool=user_pool,
    client_id="YOUR_ACTUAL_GOOGLE_CLIENT_ID",
    client_secret="YOUR_ACTUAL_GOOGLE_CLIENT_SECRET",
    # ...
)

# Apple Identity Provider
apple_provider = cognito.UserPoolIdentityProviderApple(
    self,
    "AppleProvider",
    user_pool=user_pool,
    client_id="com.example.habittracker.auth",
    team_id="YOUR_TEAM_ID",
    key_id="YOUR_KEY_ID",
    private_key="-----BEGIN PRIVATE KEY-----\n...",
    # ...
)
```

### 3. コールバックURLを本番用に更新

```python
callback_urls = [
    "http://localhost:3000/auth/callback",  # 開発環境
    "https://your-production-domain.com/auth/callback",  # 本番環境
]
```

---

## API エンドポイント

### GET /auth/sso/providers

利用可能なSSOプロバイダーの一覧とログインURLを取得します。

**リクエスト:**
```http
GET /auth/sso/providers?redirect_uri=http://localhost:3000/auth/callback
```

**レスポンス:**
```json
{
  "providers": {
    "google": {
      "name": "Google",
      "icon": "🔵",
      "login_url": "https://xxx.auth.ap-northeast-1.amazoncognito.com/oauth2/authorize?identity_provider=Google&..."
    },
    "apple": {
      "name": "Apple",
      "icon": "🍎",
      "login_url": "https://xxx.auth.ap-northeast-1.amazoncognito.com/oauth2/authorize?identity_provider=SignInWithApple&..."
    }
  },
  "cognito_hosted_ui": "https://xxx.auth.ap-northeast-1.amazoncognito.com/login?..."
}
```

### GET /auth/sso/callback

OAuth認可コードをトークンに交換します。

**リクエスト:**
```http
GET /auth/sso/callback?code=AUTHORIZATION_CODE&redirect_uri=http://localhost:3000/auth/callback
```

**レスポンス:**
```json
{
  "access_token": "eyJraWQiOi...",
  "id_token": "eyJraWQiOi...",
  "refresh_token": "eyJjdHkiOi...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "user": {
    "user_id": "google_123456789",
    "email": "user@gmail.com",
    "display_name": "User Name",
    "auth_provider": "Google"
  }
}
```

### GET /auth/me

現在ログイン中のユーザー情報を取得します。

**リクエスト:**
```http
GET /auth/me
Authorization: Bearer ACCESS_TOKEN
```

**レスポンス:**
```json
{
  "user_id": "google_123456789",
  "email": "user@gmail.com",
  "display_name": "User Name",
  "timezone": "Asia/Tokyo",
  "email_verified": true,
  "user_data": {
    "level": 1,
    "total_exp": 0,
    "stats": {...}
  }
}
```

---

## フロントエンド実装例

### React + TypeScript

```tsx
import { useState, useEffect } from 'react';

interface SSOProvider {
  name: string;
  icon: string;
  login_url: string;
}

interface SSOProviders {
  providers: Record<string, SSOProvider>;
  cognito_hosted_ui: string;
}

export const LoginPage: React.FC = () => {
  const [providers, setProviders] = useState<SSOProviders | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProviders = async () => {
      const response = await fetch(
        `${API_URL}/auth/sso/providers?redirect_uri=${encodeURIComponent(window.location.origin + '/auth/callback')}`
      );
      const data = await response.json();
      setProviders(data);
      setLoading(false);
    };
    fetchProviders();
  }, []);

  const handleSSOLogin = (provider: string) => {
    if (providers?.providers[provider]) {
      window.location.href = providers.providers[provider].login_url;
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="login-page">
      <h1>ログイン</h1>
      
      {/* 従来のメール+パスワードログイン */}
      <form onSubmit={handleEmailLogin}>
        <input type="email" placeholder="メールアドレス" />
        <input type="password" placeholder="パスワード" />
        <button type="submit">ログイン</button>
      </form>
      
      <div className="divider">または</div>
      
      {/* SSOボタン */}
      <div className="sso-buttons">
        <button onClick={() => handleSSOLogin('google')} className="google-btn">
          🔵 Googleでログイン
        </button>
        <button onClick={() => handleSSOLogin('apple')} className="apple-btn">
          🍎 Appleでログイン
        </button>
      </div>
    </div>
  );
};
```

### コールバックハンドラー

```tsx
// /auth/callback ページ
export const AuthCallbackPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const errorParam = urlParams.get('error');

      if (errorParam) {
        setError(urlParams.get('error_description') || 'ログインに失敗しました');
        return;
      }

      if (!code) {
        setError('認可コードがありません');
        return;
      }

      try {
        const response = await fetch(
          `${API_URL}/auth/sso/callback?code=${code}&redirect_uri=${encodeURIComponent(window.location.origin + '/auth/callback')}`
        );
        
        if (!response.ok) {
          throw new Error('トークンの取得に失敗しました');
        }

        const data = await response.json();
        
        // トークンを保存
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        
        // ホームにリダイレクト
        window.location.href = '/';
      } catch (err) {
        setError(err.message);
      }
    };

    handleCallback();
  }, []);

  if (error) {
    return <div className="error">{error}</div>;
  }

  return <div>ログイン中...</div>;
};
```

---

## トラブルシューティング

### よくあるエラー

| エラー | 原因 | 解決方法 |
|-------|------|---------|
| `redirect_uri_mismatch` | リダイレクトURIが一致しない | Google/Apple側とCognito側のURIを確認 |
| `invalid_client` | クライアントIDが間違っている | 設定を確認 |
| `access_denied` | ユーザーがキャンセルした | エラーハンドリングを実装 |
| `invalid_grant` | 認可コードが期限切れ | 再度ログインフローを開始 |

### デバッグ方法

1. **Cognito Hosted UIを直接テスト**
   ```
   https://your-domain.auth.region.amazoncognito.com/login?client_id=XXX&response_type=code&scope=email+openid+profile&redirect_uri=http://localhost:3000/auth/callback
   ```

2. **トークンをデコード**
   [jwt.io](https://jwt.io/)でトークンの内容を確認

3. **CloudWatch Logsを確認**
   Lambda関数のログでエラー詳細を確認

---

## セキュリティに関する注意

1. **クライアントシークレットは絶対にフロントエンドに公開しない**
2. **本番環境ではHTTPSのみ使用**
3. **リダイレクトURIのホワイトリストを厳密に設定**
4. **トークンは安全に保存（HttpOnly Cookieが推奨）**
5. **CSRFトークンを使用（stateパラメータ）**
