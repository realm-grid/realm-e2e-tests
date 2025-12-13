#!/bin/bash
# Script to run E2E tests with proper environment variables
# Loads credentials from realm-admin/.env

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
ADMIN_ENV="$ROOT_DIR/realm-admin/.env"

# Check if admin .env exists
if [ ! -f "$ADMIN_ENV" ]; then
    echo "Error: $ADMIN_ENV not found"
    echo "Please create realm-admin/.env with Azure credentials"
    exit 1
fi

# Load environment variables from admin .env
echo "Loading environment variables from $ADMIN_ENV..."
set -a
source "$ADMIN_ENV"
set +a

# Export additional E2E-specific variables
export E2E_TEST=true
export NODE_ENV=production

# Change to e2e directory
cd "$SCRIPT_DIR"

# Run docker compose with environment variables passed via --env-file
echo "Starting E2E test environment..."
echo "Using AZURE_TENANT_ID: $AZURE_TENANT_ID"
echo "Using FUNCTIONS_BASE_URL: ${FUNCTIONS_BASE_URL:-https://realm-dev-api-fa.azurewebsites.net}"

# Build with no cache to ensure fresh code
echo "Building containers (no cache to ensure latest code)..."
docker compose build --no-cache

# Start admin service
echo "Starting admin service..."
docker compose up -d admin

echo "Waiting for admin to be healthy..."
docker compose run --rm e2e-tests "$@"

# Show results
EXIT_CODE=$?
echo ""
echo "Test run complete. Exit code: $EXIT_CODE"

# Cleanup (comment out to debug)
# docker compose down

exit $EXIT_CODE
