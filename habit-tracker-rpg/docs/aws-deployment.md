# AWS デプロイメントガイド

このドキュメントでは、AWS CDKを使用したHabit Tracker RPGのデプロイ方法を説明します。

## 前提条件

- AWS アカウント
- AWS CLI がインストール・設定済み
- Node.js 18+ （CDK CLI用）
- Python 3.11+

## アーキテクチャ概要

```
                    ┌─────────────┐
                    │   Cognito   │
                    │ User Pool   │
                    └──────┬──────┘
                           │
┌─────────────┐    ┌──────┴──────┐    ┌─────────────┐
│   Client    │───▶│ API Gateway │───▶│   Lambda    │
│             │    │  (REST)     │    │  Functions  │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                                      ┌──────┴──────┐
                                      │  DynamoDB   │
                                      │   Tables    │
                                      └─────────────┘
```

## セットアップ

### 1. AWS CDK のインストール

```bash
# グローバルインストール
npm install -g aws-cdk

# バージョン確認
cdk --version
```

### 2. Python 依存関係のインストール

```bash
cd habit-tracker-rpg
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. AWS 認証情報の設定

```bash
# 認証情報の設定
aws configure

# 確認
aws sts get-caller-identity
```

## デプロイ

### 1. CDK Bootstrap（初回のみ）

CDK を使用するリージョンで初めてデプロイする場合に必要です。

```bash
cdk bootstrap aws://ACCOUNT_ID/ap-northeast-1
```

### 2. スタックの合成

```bash
cd cdk
cdk synth
```

生成された CloudFormation テンプレートは `cdk.out/` ディレクトリに保存されます。

### 3. デプロイの実行

```bash
# 変更の確認
cdk diff

# デプロイ
cdk deploy --all

# 自動承認でデプロイ
cdk deploy --all --require-approval never
```

### 4. デプロイ結果の確認

デプロイ完了後、以下の出力が表示されます：

```
Outputs:
HabitTrackerRpgStack.ApiEndpoint = https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prod
HabitTrackerRpgStack.UserPoolId = ap-northeast-1_xxxxxxxxx
HabitTrackerRpgStack.UserPoolClientId = xxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 環境別設定

### 開発環境（dev）

```bash
cdk deploy -c environment=dev
```

### ステージング環境（staging）

```bash
cdk deploy -c environment=staging
```

### 本番環境（prod）

```bash
cdk deploy -c environment=prod
```

## スタック構成

### DynamoDB テーブル

| テーブル | キー構成 | 説明 |
|---------|---------|------|
| users | PK: user_id | ユーザー情報 |
| habits | PK: user_id, SK: habit_id | 習慣情報 |
| records | PK: user_id, SK: record_id | 習慣記録 |
| user-achievements | PK: user_id, SK: achievement_id | アチーブメント |
| user-jobs | PK: user_id, SK: job_id | ジョブ |

### Lambda 関数

- **認証**: sign_up, sign_in, sign_out, refresh_token, change_password
- **ユーザー**: get_my_profile, update_my_profile, get_my_stats
- **習慣**: list_habits, create_habit, get_habit, update_habit, delete_habit, archive_habit
- **記録**: list_habit_records, create_habit_record, update_record, delete_record, get_today_records
- **統計**: get_daily_stats, get_weekly_stats, get_monthly_stats
- **アチーブメント**: list_achievements, get_achievement
- **ジョブ**: list_jobs, get_job, equip_job

### API Gateway

- REST API
- Cognito Authorizer による認証
- `/auth/*` エンドポイントは認証不要

## 更新とロールバック

### スタックの更新

```bash
# コード変更後
cdk deploy
```

### ロールバック

CloudFormation コンソールからロールバックするか、以前のバージョンを再デプロイ：

```bash
git checkout <previous-commit>
cdk deploy
```

## 削除

```bash
# スタックの削除
cdk destroy --all
```

**注意**: DynamoDB テーブルは `DESTROY` 削除ポリシーが設定されていますが、本番環境では `RETAIN` に変更することを推奨します。

## コスト見積もり

### 月額見積もり（低トラフィック）

| サービス | 見積もり |
|---------|---------|
| Lambda | ~$0 (無料枠内) |
| DynamoDB | ~$1-5 |
| API Gateway | ~$0-3.50 |
| Cognito | ~$0 (50,000 MAUまで無料) |
| **合計** | **~$1-10/月** |

## セキュリティ

### IAM ポリシー

Lambda 関数には最小権限のIAMロールが付与されます：

- DynamoDB: 必要なテーブルへの CRUD 操作
- CloudWatch Logs: ログ書き込み
- Cognito: ユーザー管理操作

### API セキュリティ

- HTTPS のみ
- Cognito JWT 認証
- CORS 設定

## モニタリング

### CloudWatch メトリクス

- Lambda: Invocations, Duration, Errors
- DynamoDB: ConsumedReadCapacityUnits, ConsumedWriteCapacityUnits
- API Gateway: Count, Latency, 4xxError, 5xxError

### アラーム設定（推奨）

```python
# CDKで設定する場合
from aws_cdk import aws_cloudwatch as cloudwatch

cloudwatch.Alarm(self, "LambdaErrors",
    metric=lambda_function.metric_errors(),
    threshold=1,
    evaluation_periods=1,
)
```

## トラブルシューティング

### デプロイエラー

```bash
# スタック状態の確認
aws cloudformation describe-stacks --stack-name HabitTrackerRpgStack

# 失敗したイベントの確認
aws cloudformation describe-stack-events --stack-name HabitTrackerRpgStack
```

### Lambda エラー

```bash
# ログの確認
aws logs tail /aws/lambda/habit-tracker-get-my-profile --follow
```

### API Gateway エラー

```bash
# テストリクエスト
curl -X GET https://API_ENDPOINT/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```
