# CloudFormation ECS Fargate テンプレート

AWS ECS Fargate でコンテナアプリケーションを実行するためのCloudFormationテンプレートです。

## 概要

このテンプレートは以下のリソースを作成します：

- VPC（2つのパブリックサブネット）
- Internet Gateway
- Application Load Balancer
- ECS Cluster（Fargate）
- ECS Service / Task Definition
- CloudWatch Log Group
- 必要なIAMロール
- セキュリティグループ

## 使用方法

```bash
aws cloudformation create-stack \
  --stack-name <stack-name> \
  --template-body file://ecs-fargate.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters ParameterKey=ContainerImage,ParameterValue=<ecr-image-uri>
```

## パラメータ

| パラメータ | 説明 | デフォルト |
|-----------|------|-----------|
| Environment | 環境名 | production |
| ContainerImage | ECRイメージURI | (必須) |

## 出力

| 出力キー | 説明 |
|---------|------|
| ALBDNS | ALBのDNS名 |
| APIEndpoint | APIエンドポイントURL |
| ECSClusterName | ECSクラスター名 |
