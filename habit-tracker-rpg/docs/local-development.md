# ローカル開発ガイド

このドキュメントでは、LocalStackを使用したローカル開発環境のセットアップと利用方法を説明します。

## 前提条件

- Docker と Docker Compose がインストールされていること
- Python 3.11+ がインストールされていること
- AWS CLI がインストールされていること

## セットアップ

### 1. LocalStack の起動

```bash
cd local
./start.sh
```

起動すると以下のサービスが利用可能になります：

- **LocalStack**: http://localhost:4566
- **LocalStack Dashboard**: https://app.localstack.cloud (オプション)

### 2. AWSリソースの確認

```bash
# 環境変数の設定
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=ap-northeast-1

# DynamoDB テーブルの確認
aws --endpoint-url=http://localhost:4566 dynamodb list-tables

# Cognito ユーザープールの確認
aws --endpoint-url=http://localhost:4566 cognito-idp list-user-pools --max-results 10
```

### 3. LocalStack の停止

```bash
cd local
./stop.sh
```

## DynamoDB テーブル

ローカル環境では以下のテーブルが作成されます：

| テーブル名 | パーティションキー | ソートキー | 説明 |
|-----------|-------------------|-----------|------|
| habit-tracker-local-users | user_id | - | ユーザー情報 |
| habit-tracker-local-habits | user_id | habit_id | 習慣情報 |
| habit-tracker-local-records | user_id | record_id | 習慣記録 |
| habit-tracker-local-user-achievements | user_id | achievement_id | 解除済みアチーブメント |
| habit-tracker-local-user-jobs | user_id | job_id | 解除済みジョブ |

## Lambda関数のローカル実行

### SAM Local を使用する方法（推奨）

```bash
# SAM CLI のインストール
pip install aws-sam-cli

# ローカル API の起動
sam local start-api --docker-network localstack_default

# 個別の関数呼び出し
sam local invoke "GetUserProfile" -e events/get-user-profile.json
```

### 直接 Python で実行する方法

```bash
# 環境変数の設定
source local/.env.local

# テスト実行
python -c "
from src.handlers.users import get_my_profile

event = {
    'requestContext': {
        'authorizer': {
            'claims': {'sub': 'test-user-id'}
        }
    }
}
result = get_my_profile(event, None)
print(result)
"
```

## テストの実行

```bash
# 仮想環境のアクティベート
source .venv/bin/activate

# 全テストの実行
pytest

# 詳細出力付き
pytest -v

# 特定のテストファイル
pytest tests/test_gamification.py -v

# カバレッジレポート付き
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## デバッグ

### ログの確認

```bash
# LocalStack のログ
docker compose -f local/docker-compose.yaml logs -f
```

### DynamoDB のデータ確認

```bash
# テーブルの項目をスキャン
aws --endpoint-url=http://localhost:4566 dynamodb scan \
  --table-name habit-tracker-local-users

# 特定のアイテムを取得
aws --endpoint-url=http://localhost:4566 dynamodb get-item \
  --table-name habit-tracker-local-users \
  --key '{"user_id": {"S": "test-user-id"}}'
```

### テストデータの投入

```bash
# ユーザーの作成
aws --endpoint-url=http://localhost:4566 dynamodb put-item \
  --table-name habit-tracker-local-users \
  --item '{
    "user_id": {"S": "test-user-001"},
    "email": {"S": "test@example.com"},
    "level": {"N": "1"},
    "total_exp": {"N": "0"},
    "created_at": {"S": "2024-01-01T00:00:00Z"}
  }'
```

## トラブルシューティング

### LocalStack が起動しない

```bash
# Docker の状態確認
docker ps

# LocalStack のコンテナを再起動
docker compose -f local/docker-compose.yaml down
docker compose -f local/docker-compose.yaml up -d
```

### DynamoDB テーブルが見つからない

```bash
# 初期化スクリプトを手動で実行
docker exec -it localstack /opt/code/localstack/init-aws.sh
```

### 権限エラーが発生する

ローカル環境では認証がモックされていることを確認してください：

```python
# conftest.py で設定される環境変数
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
```

## 環境変数一覧

| 変数名 | ローカル値 | 説明 |
|--------|-----------|------|
| `AWS_ACCESS_KEY_ID` | test | AWSアクセスキー |
| `AWS_SECRET_ACCESS_KEY` | test | AWSシークレットキー |
| `AWS_DEFAULT_REGION` | ap-northeast-1 | AWSリージョン |
| `DYNAMODB_ENDPOINT_URL` | http://localhost:4566 | DynamoDBエンドポイント |
| `COGNITO_ENDPOINT_URL` | http://localhost:4566 | Cognitoエンドポイント |
| `USERS_TABLE` | habit-tracker-local-users | ユーザーテーブル |
| `HABITS_TABLE` | habit-tracker-local-habits | 習慣テーブル |
| `RECORDS_TABLE` | habit-tracker-local-records | 記録テーブル |
