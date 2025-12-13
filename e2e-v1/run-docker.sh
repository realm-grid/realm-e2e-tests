#!/bin/bash
# Run E2E tests in Docker containers
# This avoids port conflicts with locally running services

set -e

cd "$(dirname "$0")"

echo "🐳 RealmGrid E2E Tests - Docker Runner"
echo "======================================="

# Enable BuildKit for better caching
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Cleaning up containers...${NC}"
    docker compose down --remove-orphans 2>/dev/null || true
}

# Set trap for cleanup
trap cleanup EXIT

# Parse arguments
REBUILD=""
KEEP_RUNNING=""
TEST_FILTER=""
NO_CACHE=""

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --rebuild) REBUILD="--build" ;;
        --no-cache) NO_CACHE="--no-cache" ;;
        --keep) KEEP_RUNNING="true" ;;
        --filter) TEST_FILTER="$2"; shift ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --rebuild    Force rebuild of containers"
            echo "  --no-cache   Rebuild without using cache"
            echo "  --keep       Keep containers running after tests"
            echo "  --filter     Run only tests matching pattern"
            echo "  -h, --help   Show this help"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# Create cache directory
mkdir -p /tmp/.buildx-cache/functions /tmp/.buildx-cache/admin /tmp/.buildx-cache/e2e

# Stop any existing containers
echo -e "${YELLOW}Stopping any existing E2E containers...${NC}"
docker compose down --remove-orphans 2>/dev/null || true

# Build containers
echo -e "\n${BLUE}Building containers (with cache)...${NC}"
if [ -n "$NO_CACHE" ]; then
    docker compose build --no-cache
else
    docker compose build
fi

echo -e "\n${YELLOW}Starting services...${NC}"
docker compose up -d functions admin

# Wait for services to be healthy
echo -e "\n${YELLOW}Waiting for services to be healthy...${NC}"
echo -n "Functions API: "
for i in {1..60}; do
    if docker compose exec -T functions curl -sf http://localhost:7071/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}Ready!${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

echo -n "Admin Frontend: "
for i in {1..60}; do
    if docker compose exec -T admin curl -sf http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}Ready!${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Run tests
echo -e "\n${YELLOW}Running E2E tests...${NC}"
echo "======================================="

TEST_CMD="npx playwright test --reporter=list"
if [ -n "$TEST_FILTER" ]; then
    TEST_CMD="$TEST_CMD --grep='$TEST_FILTER'"
fi

docker compose run --rm e2e-tests $TEST_CMD
TEST_EXIT_CODE=$?

# Show results
echo ""
echo "======================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
fi

# View report
echo -e "\n${YELLOW}Test artifacts saved to:${NC}"
echo "  - playwright-report/ (HTML report)"
echo "  - test-results/ (screenshots, videos, traces)"

echo -e "\n${YELLOW}To view the HTML report:${NC}"
echo "  npx playwright show-report playwright-report"

# Keep running if requested
if [ "$KEEP_RUNNING" = "true" ]; then
    echo -e "\n${YELLOW}Containers are still running. Stop with:${NC}"
    echo "  docker compose down"
    trap - EXIT  # Remove cleanup trap
fi

exit $TEST_EXIT_CODE
