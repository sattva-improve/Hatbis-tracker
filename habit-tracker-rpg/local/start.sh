#!/bin/bash
# Start LocalStack for local development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting LocalStack..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start LocalStack
docker compose up -d

echo "⏳ Waiting for LocalStack to be ready..."
sleep 10

# Check if LocalStack is healthy
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:4566/_localstack/health | grep -q '"dynamodb": "running"'; then
        echo "✅ LocalStack is ready!"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "Waiting... ($ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ LocalStack failed to start"
    exit 1
fi

# Load environment variables
source .env.local

# Get configuration from LocalStack
echo ""
echo "📋 LocalStack Configuration:"
echo "================================"
echo "Endpoint URL: http://localhost:4566"
echo ""
echo "DynamoDB Tables:"
awslocal dynamodb list-tables --endpoint-url http://localhost:4566 --region ap-northeast-1 2>/dev/null || echo "Tables will be created on first run"
echo ""
echo "To use with your application, set these environment variables:"
echo "  export AWS_ACCESS_KEY_ID=test"
echo "  export AWS_SECRET_ACCESS_KEY=test"
echo "  export DYNAMODB_ENDPOINT_URL=http://localhost:4566"
echo ""
echo "Or source the .env.local file:"
echo "  source .env.local"
echo ""
echo "✅ LocalStack is running!"
