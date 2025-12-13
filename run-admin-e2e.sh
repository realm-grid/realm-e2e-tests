#!/bin/bash
# Run admin portal E2E tests in Docker
set -e

echo "═══════════════════════════════════════════════"
echo "🧪 RealmGrid Admin Portal E2E Tests"
echo "═══════════════════════════════════════════════"

# Check if admin portal is running
echo "🔍 Checking if admin portal is running on http://localhost:4321..."
if curl -s -f http://localhost:4321 > /dev/null 2>&1; then
    echo "✅ Admin portal is running"
else
    echo "❌ Admin portal is not running on http://localhost:4321"
    echo "Please start the admin portal first:"
    echo "  cd realm-admin && npm run dev"
    exit 1
fi

# Create reports directory
mkdir -p reports/screenshots reports/cucumber

echo ""
echo "🐳 Building Docker image..."
docker build -f Dockerfile.fast -t realm-e2e-admin:latest . --quiet

echo ""
echo "🚀 Running E2E tests..."
docker run --rm \
    --network host \
    -v "$(pwd)/reports:/app/reports" \
    -e ADMIN_URL=http://localhost:4321 \
    -e HEADLESS=true \
    realm-e2e-admin:latest

echo ""
echo "═══════════════════════════════════════════════"
echo "✅ Tests completed!"
echo "📊 Results: reports/cucumber/results.json"
echo "📸 Screenshots: reports/screenshots/"
echo "═══════════════════════════════════════════════"
