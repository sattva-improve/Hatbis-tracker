#!/bin/bash
# Stop LocalStack

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Stopping LocalStack..."
docker compose down

echo "✅ LocalStack stopped!"
