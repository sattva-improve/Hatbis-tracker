# AWS IAM ポリシー - 自動デプロイ用

本ディレクトリには、AWSリソースを使用した自動デプロイのためのIAMポリシーファイルが含まれています。

## ポリシー一覧

| ファイル名 | 説明 | 用途 |
|-----------|------|-----|
| `auto-deploy-full-access-policy.json` | フルアクセスポリシー | 開発環境用、全AWSサービスへの包括的なアクセス |
| `trust-policy.json` | 信頼ポリシー | IAMロールに付与するサービス信頼関係 |
| `github-actions-trust-policy.json` | GitHub Actions用信頼ポリシー | OIDC経由でのGitHub Actionsからの認証 |
| `cicd-pipeline-policy.json` | CI/CDパイプラインポリシー | CodePipeline, CodeBuild, CodeDeploy用 |
| `cloudformation-deployment-policy.json` | CloudFormationポリシー | IaC用の包括的な権限 |
| `ecs-deployment-policy.json` | ECSデプロイメントポリシー | ECS/Fargateへのデプロイ用 |
| `ecs-task-execution-role-policy.json` | ECSタスク実行ロールポリシー | ECSタスク起動時に使用 |
| `ecs-task-role-policy.json` | ECSタスクロールポリシー | 実行中のコンテナがAWSリソースにアクセス |

## 使用方法

### 1. IAMロールの作成

```bash
# 信頼ポリシーを使用してロールを作成
aws iam create-role \
  --role-name AutoDeployRole \
  --assume-role-policy-document file://trust-policy.json

# ポリシーをアタッチ
aws iam put-role-policy \
  --role-name AutoDeployRole \
  --policy-name AutoDeployPolicy \
  --policy-document file://auto-deploy-full-access-policy.json
```

### 2. GitHub Actions用OIDC設定

```bash
# OIDCプロバイダーの作成（初回のみ）
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  --client-id-list sts.amazonaws.com

# GitHub Actions用ロールの作成
# ※ github-actions-trust-policy.json の ACCOUNT_ID, GITHUB_ORG, REPO_NAME を置換してから実行
aws iam create-role \
  --role-name GitHubActionsDeployRole \
  --assume-role-policy-document file://github-actions-trust-policy.json

aws iam put-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-name GitHubActionsDeployPolicy \
  --policy-document file://cicd-pipeline-policy.json
```

### 3. ECSタスク用ロールの作成

```bash
# タスク実行ロール
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

aws iam put-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-name ecsTaskExecutionPolicy \
  --policy-document file://ecs-task-execution-role-policy.json

# タスクロール（アプリケーション用）
aws iam create-role \
  --role-name ecsTaskRole \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

aws iam put-role-policy \
  --role-name ecsTaskRole \
  --policy-name ecsTaskPolicy \
  --policy-document file://ecs-task-role-policy.json
```

## 環境別推奨構成

### 開発環境
- `auto-deploy-full-access-policy.json` を使用
- 迅速な開発・テストのため、広範な権限を付与

### ステージング環境
- `cicd-pipeline-policy.json` + `ecs-deployment-policy.json` を組み合わせ
- 本番に近い権限設定でテスト

### 本番環境
- 最小権限の原則に基づき、必要な権限のみを付与
- 各ポリシーから必要なアクションのみを抽出して使用
- リソースARNを明示的に指定することを推奨

## セキュリティ考慮事項

⚠️ **重要**: これらのポリシーは汎用性を優先して設計されており、必要以上に広い権限が含まれています。

### 本番環境での使用前に必ず以下を実施してください：

1. **リソースの制限**: `"Resource": "*"` を具体的なARNに変更
2. **アクションの絞り込み**: 不要なアクションを削除
3. **条件の追加**: IPアドレス制限、MFA要件などを追加
4. **定期的な監査**: AWS IAM Access Analyzerを使用して権限を確認

### 例: リソース制限の追加

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": [
    "arn:aws:s3:::my-deploy-bucket/*",
    "arn:aws:s3:::my-artifact-bucket/*"
  ]
}
```

## 関連ドキュメント

- [AWS IAM ベストプラクティス](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [最小権限の原則](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege)
- [IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)
