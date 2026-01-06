#!/bin/bash
# AWS ECS デプロイスクリプト
# Task Management API をAWS App Runner にデプロイ

set -e

# 変数設定
AWS_REGION="ap-northeast-1"
APP_NAME="task-management-api"
ECR_REPO_NAME="${APP_NAME}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "=========================================="
echo "Task Management API - AWS Deploy"
echo "=========================================="
echo "AWS Account: ${ACCOUNT_ID}"
echo "Region: ${AWS_REGION}"
echo "ECR URI: ${ECR_URI}"
echo ""

# Step 1: ECRリポジトリの作成
echo "[1/5] Creating ECR repository..."
aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${AWS_REGION} 2>/dev/null || \
aws ecr create-repository \
    --repository-name ${ECR_REPO_NAME} \
    --region ${AWS_REGION} \
    --image-scanning-configuration scanOnPush=true \
    --image-tag-mutability MUTABLE

# Step 2: ECRへのログイン
echo "[2/5] Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Step 3: Dockerイメージのビルド
echo "[3/5] Building Docker image..."
cd /home/nekonisi/auto_deploy/backend
docker build -t ${APP_NAME}:latest .

# Step 4: イメージのタグ付けとプッシュ
echo "[4/5] Pushing image to ECR..."
docker tag ${APP_NAME}:latest ${ECR_URI}:latest
docker tag ${APP_NAME}:latest ${ECR_URI}:$(date +%Y%m%d-%H%M%S)
docker push ${ECR_URI}:latest

# Step 5: App Runnerサービスの作成/更新
echo "[5/5] Deploying to App Runner..."

# App Runner用のIAMロールを確認/作成
ROLE_NAME="AppRunnerECRAccessRole"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

# ロールが存在するか確認
if ! aws iam get-role --role-name ${ROLE_NAME} 2>/dev/null; then
    echo "Creating IAM role for App Runner..."
    
    # Trust policy
    cat > /tmp/trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "build.apprunner.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
    
    aws iam create-role \
        --role-name ${ROLE_NAME} \
        --assume-role-policy-document file:///tmp/trust-policy.json
    
    aws iam attach-role-policy \
        --role-name ${ROLE_NAME} \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess
    
    echo "Waiting for role propagation..."
    sleep 10
fi

# App Runnerサービスが存在するか確認
SERVICE_ARN=$(aws apprunner list-services --region ${AWS_REGION} \
    --query "ServiceSummaryList[?ServiceName=='${APP_NAME}'].ServiceArn" \
    --output text 2>/dev/null || echo "")

if [ -z "$SERVICE_ARN" ] || [ "$SERVICE_ARN" == "None" ]; then
    echo "Creating new App Runner service..."
    
    # サービス設定ファイル作成
    cat > /tmp/apprunner-config.json << EOF
{
    "ServiceName": "${APP_NAME}",
    "SourceConfiguration": {
        "ImageRepository": {
            "ImageIdentifier": "${ECR_URI}:latest",
            "ImageConfiguration": {
                "Port": "8000",
                "RuntimeEnvironmentVariables": {
                    "DJANGO_SETTINGS_MODULE": "config.settings",
                    "DEBUG": "False",
                    "ALLOWED_HOSTS": "*"
                }
            },
            "ImageRepositoryType": "ECR"
        },
        "AutoDeploymentsEnabled": true,
        "AuthenticationConfiguration": {
            "AccessRoleArn": "${ROLE_ARN}"
        }
    },
    "InstanceConfiguration": {
        "Cpu": "0.25 vCPU",
        "Memory": "0.5 GB"
    },
    "HealthCheckConfiguration": {
        "Protocol": "HTTP",
        "Path": "/api/v1/",
        "Interval": 10,
        "Timeout": 5,
        "HealthyThreshold": 1,
        "UnhealthyThreshold": 5
    }
}
EOF
    
    aws apprunner create-service \
        --cli-input-json file:///tmp/apprunner-config.json \
        --region ${AWS_REGION}
    
    echo "Waiting for service to be ready..."
    aws apprunner wait service-running \
        --service-arn $(aws apprunner list-services --region ${AWS_REGION} \
            --query "ServiceSummaryList[?ServiceName=='${APP_NAME}'].ServiceArn" \
            --output text) \
        --region ${AWS_REGION} 2>/dev/null || echo "Service creation in progress..."
else
    echo "Updating existing App Runner service..."
    aws apprunner start-deployment \
        --service-arn ${SERVICE_ARN} \
        --region ${AWS_REGION}
fi

# サービスURLの取得
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
SERVICE_URL=$(aws apprunner list-services --region ${AWS_REGION} \
    --query "ServiceSummaryList[?ServiceName=='${APP_NAME}'].ServiceUrl" \
    --output text 2>/dev/null || echo "pending...")
echo "Service URL: https://${SERVICE_URL}"
echo ""
echo "API Endpoints:"
echo "  - POST /api/v1/auth/register - ユーザー登録"
echo "  - POST /api/v1/auth/login    - ログイン"
echo "  - GET  /api/v1/projects      - プロジェクト一覧"
echo "  - GET  /api/v1/projects/{id}/tasks - タスク一覧"
