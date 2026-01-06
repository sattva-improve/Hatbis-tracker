#!/bin/bash
# Initialize LocalStack resources

echo "Initializing LocalStack resources for Habit Tracker RPG..."

# Wait for LocalStack to be ready
sleep 5

# Create DynamoDB tables
echo "Creating DynamoDB tables..."

# Users table
awslocal dynamodb create-table \
    --table-name habit-tracker-rpg-dev-users \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-1

# Habits table
awslocal dynamodb create-table \
    --table-name habit-tracker-rpg-dev-habits \
    --attribute-definitions \
        AttributeName=habit_id,AttributeType=S \
        AttributeName=user_id,AttributeType=S \
    --key-schema \
        AttributeName=habit_id,KeyType=HASH \
        AttributeName=user_id,KeyType=RANGE \
    --global-secondary-indexes \
        '[{
            "IndexName": "user_id-index",
            "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"}
        }]' \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-1

# Records table
awslocal dynamodb create-table \
    --table-name habit-tracker-rpg-dev-records \
    --attribute-definitions \
        AttributeName=habit_id,AttributeType=S \
        AttributeName=record_id,AttributeType=S \
        AttributeName=user_id,AttributeType=S \
        AttributeName=completed_date,AttributeType=S \
    --key-schema \
        AttributeName=habit_id,KeyType=HASH \
        AttributeName=record_id,KeyType=RANGE \
    --global-secondary-indexes \
        '[{
            "IndexName": "user_id-index",
            "KeySchema": [
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "completed_date", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }]' \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-1

# User Achievements table
awslocal dynamodb create-table \
    --table-name habit-tracker-rpg-dev-user-achievements \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=achievement_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=achievement_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-1

# User Jobs table
awslocal dynamodb create-table \
    --table-name habit-tracker-rpg-dev-user-jobs \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=job_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=job_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-1

echo "DynamoDB tables created successfully!"

# Create Cognito User Pool
echo "Creating Cognito User Pool..."

USER_POOL_ID=$(awslocal cognito-idp create-user-pool \
    --pool-name habit-tracker-rpg-dev-users \
    --auto-verified-attributes email \
    --policies '{"PasswordPolicy":{"MinimumLength":8,"RequireUppercase":true,"RequireLowercase":true,"RequireNumbers":true,"RequireSymbols":false}}' \
    --schema '[
        {"Name":"email","Required":true,"Mutable":true,"AttributeDataType":"String"},
        {"Name":"custom:display_name","Mutable":true,"AttributeDataType":"String"},
        {"Name":"custom:timezone","Mutable":true,"AttributeDataType":"String"}
    ]' \
    --region ap-northeast-1 \
    --query 'UserPool.Id' \
    --output text)

echo "User Pool created: $USER_POOL_ID"

# Create User Pool Client
CLIENT_ID=$(awslocal cognito-idp create-user-pool-client \
    --user-pool-id "$USER_POOL_ID" \
    --client-name habit-tracker-rpg-dev-client \
    --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH ALLOW_USER_SRP_AUTH \
    --region ap-northeast-1 \
    --query 'UserPoolClient.ClientId' \
    --output text)

echo "User Pool Client created: $CLIENT_ID"

# Save configuration
cat > /var/lib/localstack/habit-tracker-config.json << EOF
{
    "user_pool_id": "$USER_POOL_ID",
    "client_id": "$CLIENT_ID",
    "region": "ap-northeast-1"
}
EOF

echo "Configuration saved to /var/lib/localstack/habit-tracker-config.json"
echo "LocalStack initialization complete!"
