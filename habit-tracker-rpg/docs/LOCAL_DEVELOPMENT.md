# ローカル開発環境セットアップガイド

このドキュメントでは、LocalStackを使用したHabit Tracker RPGのローカル開発環境のセットアップ方法を説明します。

## 📋 前提条件

- Docker & Docker Compose
- Python 3.11+
- AWS CLI (ローカル確認用)
- curl または httpie (APIテスト用)

---

## 🚀 クイックスタート

### 1. Docker環境の起動

```bash
cd habit-tracker-rpg/local

# LocalStackを起動
./start.sh

# または直接docker-composeを使用
docker compose up -d
```

### 2. 起動確認

```bash
# コンテナの状態確認
docker compose ps

# LocalStackのヘルスチェック
curl http://localhost:4566/_localstack/health
```

### 3. 環境の停止

```bash
./stop.sh

# または
docker compose down
```

---

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                    LocalStack                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  DynamoDB   │  │   Lambda    │  │ API Gateway │     │
│  │   Tables    │  │  Functions  │  │   REST API  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│  ┌─────────────┐  ┌─────────────┐                      │
│  │   Cognito   │  │     IAM     │                      │
│  │  UserPool   │  │    Roles    │                      │
│  └─────────────┘  └─────────────┘                      │
│                                                         │
│  Port: 4566 (Gateway)                                  │
│  Ports: 4510-4559 (Additional Services)                │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 ディレクトリ構成

```
local/
├── docker-compose.yaml    # Docker Compose設定
├── start.sh               # 起動スクリプト
├── stop.sh                # 停止スクリプト
└── init-scripts/
    └── init-aws.sh        # AWS リソース初期化スクリプト
```

---

## ⚙️ 設定詳細

### docker-compose.yaml

```yaml
version: '3.8'

services:
  localstack:
    image: localstack/localstack:3.0
    ports:
      - "4566:4566"           # Gateway ポート
      - "4510-4559:4510-4559" # サービス用ポート
    environment:
      - SERVICES=dynamodb,lambda,apigateway,cognito-idp,iam,logs,s3
      - DEBUG=1
      - PERSISTENCE=1
      - LAMBDA_EXECUTOR=local
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "./init-scripts:/etc/localstack/init/ready.d"
      - "./data:/var/lib/localstack"
      - "/var/run/docker.sock:/var/run/docker.sock"
```

### 環境変数

| 変数 | 値 | 説明 |
|------|-----|------|
| SERVICES | dynamodb,lambda,apigateway,cognito-idp,iam,logs,s3 | 有効化するAWSサービス |
| DEBUG | 1 | デバッグモード有効 |
| PERSISTENCE | 1 | データ永続化有効 |
| LAMBDA_EXECUTOR | local | Lambdaの実行モード |

---

## 🗄️ DynamoDB テーブル

LocalStack起動時に以下のテーブルが自動作成されます：

### habit-tracker-rpg-dev-users

ユーザー情報を格納するテーブル。

```
Primary Key: user_id (S)
GSI: email-index (email)
```

### habit-tracker-rpg-dev-habits

習慣情報を格納するテーブル。

```
Primary Key: habit_id (S)
GSI: user-index (user_id)
GSI: user-category-index (user_id, category)
```

### habit-tracker-rpg-dev-records

習慣達成記録を格納するテーブル。

```
Primary Key: record_id (S)
GSI: habit-date-index (habit_id, completed_date)
GSI: user-date-index (user_id, completed_date)
```

### habit-tracker-rpg-dev-user-achievements

ユーザーのアチーブメント解除状況を格納するテーブル。

```
Primary Key: user_id (S), achievement_id (S)
```

### habit-tracker-rpg-dev-user-jobs

ユーザーのジョブ解除状況を格納するテーブル。

```
Primary Key: user_id (S), job_id (S)
```

---

## 🔐 Cognito 設定

LocalStack起動時にCognitoユーザープールが作成されます：

```bash
# ユーザープール情報
Pool Name: habit-tracker-rpg-dev-pool
Pool ID: ap-northeast-1_xxxxxxxxx

# クライアント情報
Client Name: habit-tracker-rpg-dev-client
Client ID: xxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🧪 動作確認

### AWS CLI での確認

LocalStackのエンドポイントを指定してAWS CLIを使用できます：

```bash
# エンドポイントURL
export AWS_ENDPOINT_URL=http://localhost:4566

# DynamoDBテーブル一覧
aws dynamodb list-tables --endpoint-url $AWS_ENDPOINT_URL

# テーブル詳細
aws dynamodb describe-table \
  --table-name habit-tracker-rpg-dev-users \
  --endpoint-url $AWS_ENDPOINT_URL

# Cognitoユーザープール一覧
aws cognito-idp list-user-pools \
  --max-results 10 \
  --endpoint-url $AWS_ENDPOINT_URL
```

### awslocalコマンドの使用

LocalStack CLIをインストールすると、`awslocal`コマンドが使用できます：

```bash
# インストール
pip install awscli-local

# 使用例
awslocal dynamodb list-tables
awslocal cognito-idp list-user-pools --max-results 10
```

---

## 📡 API テスト

### curlでのテスト

```bash
# ベースURL
BASE_URL=http://localhost:4566/restapis/<api-id>/dev/_user_request_

# ユーザー登録
curl -X POST "$BASE_URL/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "display_name": "テストユーザー"
  }'

# ログイン
curl -X POST "$BASE_URL/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### httpieでのテスト

```bash
# ユーザー登録
http POST localhost:4566/.../auth/signup \
  email=test@example.com \
  password=SecurePass123! \
  display_name=テストユーザー
```

---

## 🐛 トラブルシューティング

### LocalStackが起動しない

```bash
# Dockerログの確認
docker compose logs localstack

# コンテナの再起動
docker compose restart localstack
```

### テーブルが作成されない

```bash
# 初期化スクリプトの手動実行
docker compose exec localstack /etc/localstack/init/ready.d/init-aws.sh

# または直接awslocalで作成
awslocal dynamodb create-table \
  --table-name habit-tracker-rpg-dev-users \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### ポートが使用中

```bash
# 使用中のポートを確認
lsof -i :4566

# 別のポートを使用
# docker-compose.yamlのportsを編集
ports:
  - "4567:4566"
```

### データをリセットしたい

```bash
# 停止してデータを削除
docker compose down -v
rm -rf ./data

# 再起動
docker compose up -d
```

---

## 🔧 カスタマイズ

### 追加のAWSサービスを有効化

```yaml
# docker-compose.yaml
environment:
  - SERVICES=dynamodb,lambda,apigateway,cognito-idp,iam,logs,s3,sqs,sns
```

### Lambda関数のホットリロード

開発中はLambda関数をローカルから直接実行できます：

```bash
# Python仮想環境をアクティベート
source .venv/bin/activate

# 環境変数を設定
export DYNAMODB_ENDPOINT_URL=http://localhost:4566
export COGNITO_ENDPOINT_URL=http://localhost:4566

# ハンドラーを直接テスト
python -c "
from src.handlers.auth import sign_up
event = {
    'body': '{\"email\": \"test@example.com\", \"password\": \"Test123!\", \"display_name\": \"Test\"}'
}
result = sign_up(event, {})
print(result)
"
```

---

## 📚 参考リンク

- [LocalStack Documentation](https://docs.localstack.cloud/)
- [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
