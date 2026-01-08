# Habit Tracker RPG ドキュメント

## 📚 ドキュメント一覧

### 概要・入門

| ドキュメント | 説明 |
|-------------|------|
| [README.md](../README.md) | プロジェクト概要とクイックスタート |

### API リファレンス

| ドキュメント | 説明 |
|-------------|------|
| [API_REFERENCE.md](./API_REFERENCE.md) | 全APIエンドポイントの詳細（リクエスト/レスポンス例付き） |
| [openapi.yaml](./openapi.yaml) | OpenAPI 3.0 仕様書 |

### システム設計

| ドキュメント | 説明 |
|-------------|------|
| [GAMIFICATION.md](./GAMIFICATION.md) | ゲーミフィケーションシステム設計書（経験値、レベル、アチーブメント、ジョブ） |

### 開発ガイド

| ドキュメント | 説明 |
|-------------|------|
| [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md) | LocalStackを使ったローカル開発環境のセットアップ |

### APIサンプル

| ドキュメント | 説明 |
|-------------|------|
| [api-examples/api_examples.json](./api-examples/api_examples.json) | 全APIのリクエスト/レスポンスサンプル（JSON形式） |

---

## 🗂️ ドキュメント構成

```
docs/
├── index.md                    # このファイル
├── API_REFERENCE.md            # API リファレンス
├── GAMIFICATION.md             # ゲーミフィケーション設計
├── LOCAL_DEVELOPMENT.md        # ローカル開発ガイド
├── openapi.yaml                # OpenAPI 仕様
└── api-examples/
    └── api_examples.json       # APIサンプル集
```

---

## 🎯 クイックリンク

### 認証系API

- [POST /auth/signup - ユーザー登録](./API_REFERENCE.md#post-authsignup---ユーザー登録)
- [POST /auth/signin - ログイン](./API_REFERENCE.md#post-authsignin---ログイン)
- [POST /auth/signout - ログアウト](./API_REFERENCE.md#post-authsignout---ログアウト)

### 習慣管理API

- [GET /habits - 習慣一覧取得](./API_REFERENCE.md#get-habits---習慣一覧取得)
- [POST /habits - 習慣作成](./API_REFERENCE.md#post-habits---習慣作成)
- [POST /habits/{habitId}/records - 記録作成](./API_REFERENCE.md#post-habitshabitidrecords---習慣記録作成達成報告)

### ゲーミフィケーション

- [ステータスシステム](./GAMIFICATION.md#⚔️-ステータスシステム)
- [経験値システム](./GAMIFICATION.md#📈-経験値システム)
- [レベルシステム](./GAMIFICATION.md#📊-レベルシステム)
- [アチーブメント](./GAMIFICATION.md#🏆-アチーブメントシステム)
- [ジョブシステム](./GAMIFICATION.md#👔-ジョブシステム)

---

## 📝 更新履歴

| 日付 | 変更内容 |
|------|----------|
| 2026-01-08 | 初版作成、API リファレンス、ゲーミフィケーション設計、ローカル開発ガイドを追加 |
