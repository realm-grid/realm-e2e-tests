#!/bin/bash
# Run admin portal E2E tests locally (no Docker)
set -e

echo "═══════════════════════════════════════════════"
echo "🧪 RealmGrid Admin Portal E2E Tests (Local)"
echo "═══════════════════════════════════════════════"

# Check if in venv
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "🔧 Activating virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
fi

# Create reports directory
mkdir -p reports/screenshots reports/cucumber

echo ""
echo "🚀 Running E2E tests..."
export ADMIN_URL=http://localhost:4321
export HEADLESS=false

behave features/admin/production-data.feature \
    --format=json \
    --outfile=reports/cucumber/results.json \
    --format=pretty \
    --no-capture \
    -v

echo ""
echo "═══════════════════════════════════════════════"
echo "✅ Tests completed!"
echo "📊 Results: reports/cucumber/results.json"
echo "📸 Screenshots: reports/screenshots/"
echo "═══════════════════════════════════════════════"
